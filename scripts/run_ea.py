from deap import base, creator, tools, algorithms
from scoop import futures
import pandas as pd
import numpy as np
import datetime
from swmmio import swmmio
import random
import os
from shutil import copyfile
import subprocess
from update_process_model_input_file import update_controls
from run_swmm_mpc import input_process_file_inp, input_process_file_base, control_time_step, \
        control_str_id

input_process_file_inp = "../simple_model/simple_smart_blank_tst.inp"
input_process_file_base  = "../simple_model/simple_smart_blank_tst"
FNULL = open(os.devnull, 'w')

def evaluate(individual):
    # make process model tmp file
    input_tmp_process_file_base = input_process_file_base + "_tmp"
    input_tmp_process_inp = input_tmp_process_file_base + ".inp"
    copyfile(input_process_file_inp, input_tmp_process_inp)

    # convert individual to percentages
    indivi_percentage = [setting/10. for setting in individual]
    policies = {control_str_id: indivi_percentage}

    # update controls
    update_controls(input_tmp_process_inp, control_time_step, policies)

    # run the swmm model
    cmd = "swmm5.exe {0}.inp {0}.rpt".format(input_tmp_process_file_base)
    subprocess.call(cmd, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

    # read the output file
    mymodel = swmmio.Model(input_tmp_process_inp)
    nodes = mymodel.nodes()
    nodes.fillna(0, inplace=True)
    storage_flood_volume = nodes.loc['St1']['TotalFloodVol']
    node_flood_volume = nodes.loc['J3']['TotalFloodVol']
    target_storage_level = 1.
    avg_dev_fr_tgt_st_lvl = nodes.loc['St1', 'AvgDepth'] - target_storage_level

    # convert the contents of the output file into a cost
    cost = 2 * storage_flood_volume**3 + node_flood_volume*2 + avg_dev_fr_tgt_st_lvl 
    return cost,

creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
creator.create('Individual', list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("map", futures.map)
toolbox.register("attr_int", random.randint, 0, 10)
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attr_int, 24)
toolbox.register('population', tools.initRepeat, list, toolbox.individual)
toolbox.register('evaluate', evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutUniformInt, low=0, up=10, indpb=0.10)
toolbox.register("select", tools.selTournament, tournsize=6)

def main():
    ngen = 10
    nindividuals = 80
    pop = toolbox.population(n=nindividuals)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)
    beg_time = datetime.datetime.now().strftime("%Y.%m.%d.%H.%M")
    f = open('log.txt', 'a')
    f.write('run started: {}'.format(beg_time))
    pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=ngen, stats=stats,
                                       halloffame=hof, verbose=True)
    end_time = datetime.datetime.now().strftime("%Y.%m.%d.%H.%M")
    f.write('run ended: {}\n'.format(end_time))
    f.close()

    df = pd.DataFrame(logbook)
    df.to_csv('results_{}csv'.format(end_time, index=False))

    f = open('hof.txt', 'a')
    for h in hof:
        f.write('hof for {}:{}    fitness:{}\n'.format(end_time, h, h.fitness))
    f.close()

if __name__ == "__main__":
    main()

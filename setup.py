from setuptools import setup, find_packages

setup(name='swmm_mpc',
      version = '0.1',
      description = 'model predictive control for swmm5 models',
      url = 'https://github.com/uva-hydroinformatics-group/swmm_mpc',
      author = 'Jeffrey Sadler',
      author_email = 'jms3fb@virginia.edu',
      license = 'MIT',
      packages = find_packages(),
      install_requires=[
          'pandas',
          'matplotlib',
          'swmmio',
          'scoop',
          'numpy',
          'deap',
          ]
      dependency_links=[
          'https://github.com/uva-hydroinformatics/pyswmm',
          ]
      )


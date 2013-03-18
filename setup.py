from setuptools import setup

setup(name='caprice',
      version='0.1',
      description='Redis-based caching of models to improve performance of getting a random item',
      author='Siddharth Sarda',
      author_email='siddharthsarda01@gmail.com',
      url='https://github.com/siddharthsarda/caprice',
      packages = ['caprice'],
      package_dir= { 'caprice' : 'caprice' },
      install_requires=['django','redis'],
     )

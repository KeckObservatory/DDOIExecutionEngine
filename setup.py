from setuptools import setup, find_packages


setup(
    name = "execution_engine",
    # packages=find_packages(where='execution_engine'),
    packages=['execution_engine', 
              'execution_engine.core', 
              'execution_engine.interface', 
              'execution_engine.core', 
              'execution_engine.configs', 
              'execution_engine.core.Queues',
              'execution_engine.core.Queues.SequenceQueue',
              'execution_engine.core.Queues.ObservingQueue',
              'execution_engine.core.Queues.EventQueue'],
    package_data={'': ['*.json']},
    # package_dir={"": "execution_engine"},
    version='1.0.0'
)

#!/usr/bin/python

"""Setup the py7zip project"""
import os
import setuptools

__version__ = '0.1'

PROJECT_ROOT=os.path.dirname(os.path.realpath(__file__))
PYTHON_LIB_DIR=os.path.join(PROJECT_ROOT, 'pylib')
PYTHON_SCRIPTS_DIR=os.path.join(PROJECT_ROOT, 'src', 'bin', 'scripts')
PYTHON_TEST_DIR=os.path.join(PROJECT_ROOT, 'test')

class PostBuildCommand(setuptools.Command):
    """Custom post build clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -rf {0}/*.egg-info {0}/.eggs $(find {0} -name __pycache__)  $(find {0} -name _deps)'.format(PROJECT_ROOT))

class CleanCommand(setuptools.Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -rf {0}/.coverage {0}/htmlcov {1}/.tox'.format(PYTHON_TEST_DIR, PROJECT_ROOT))
        PostBuildCommand.run(self)

setuptools.setup(
    name='py7zip',
    version=__version__,
    description='Python 7zip',
    packages=setuptools.find_namespace_packages(exclude=['_vendor', '_deps', 'tests']),

    cmdclass={
        'clean': CleanCommand,
        'post_build': PostBuildCommand,
    }

)

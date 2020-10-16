import os

# Setup run environment
os.environ['PYTEST_ROOT'] = os.path.dirname(__file__)
os.environ['MOCK_ROOT'] = os.path.join(os.environ['PYTEST_ROOT'], 'mock')

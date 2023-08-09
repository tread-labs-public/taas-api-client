from setuptools import setup, find_packages

setup(
    name='taas-api-client',
    version='0.1',
    packages=find_packages(),
    description='API client for TAAS web app',
    url='https://github.com/tread-labs-public/taas-api-client.git',
    author='Tread Labs',
    install_requires=[
        'requests'
    ],
)

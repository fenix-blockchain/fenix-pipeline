import os

import setuptools


os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open('README.md') as fin:
    README = fin.read()

install_dependencies = (
    'websockets>=8.0.2',
)

test_dependencies = (
    'mock',
)


setuptools.setup(
    name='fenix-pipeline-sdk',
    version='0.9.1',
    author='Fenix Blockchain Technology',
    author_email='support@fenixblockchain.com',
    description='SDK for interacting with the Fenix Pipeline API',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/fenix-blockchain/fenix-pipeline',
    packages=setuptools.find_packages(),
    license='MIT License',
    keywords='fenix pipeline sdk',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Topic :: Office/Business :: Financial',
    ],
    python_requires='>=3.7',
    install_requires=install_dependencies,
    tests_require=install_dependencies + test_dependencies,
)

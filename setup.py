from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='mma_correlator',
    version='1.0.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A prototype for correlating multi-messenger astrophysical events.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/your-username/mma_project', # Replace with your repo URL
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Astronomy',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'run-correlator = mma_correlator.correlator:main',
        ],
    },
)
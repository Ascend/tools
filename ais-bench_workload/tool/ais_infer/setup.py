from setuptools import setup, find_packages  # type: ignore

with open('requirements.txt', encoding='utf-8') as f:
    required = f.read().splitlines()

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ais_bench',
    version='0.0.2',
    description='ais_bench tool',
    long_description=long_description,
    url='ais_bench url',
    packages=find_packages(),
    keywords='ais_bench tool',
    install_requires=required,
    python_requires='>=3.7'
)
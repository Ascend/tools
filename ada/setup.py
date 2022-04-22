import setuptools
from ada import VERSION as ada_version

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ada",
    version=ada_version,
    author="shengnan",
    author_email="titan.sheng@huawei.com",
    description="Ascend debugging assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://codehub-y.huawei.com/s00538840/ada",
    project_urls={
        "Bug Tracker": "https://codehub-y.huawei.com/s00538840/ada/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    py_modules=['ada_cmd', 'ada_prof_cmd'],
    packages=setuptools.find_packages(include=["ada", "ada.*"]),
    python_requires=">=3.6",
    install_requires=[
        'hdfs>=2.6.0',
    ],
    entry_points={
        'console_scripts': [
            'ada=ada_cmd:main',
            'ada-pa=ada_prof_cmd:main'
        ]
    }
)

# python setup.py sdist bdist_wheel

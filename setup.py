import io
import os

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

# Avoids IDE errors, but actual version is read from version.py
__version__ = None
exec(open('api/version.py').read())

# Get the long description from the README file
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    'numpy >= 1.12.1'
]

extras_requires = {
    'tests': [
        'coverage >= 4.3.4',
        'codecov >= 2.0.15',
        'pytest >= 3.0.3',
        'pytest-cov >= 2.4.0',
        'flake8 >= 3.0.0',
        'flake8_docstrings >= 1.0.2'],
}


setup(
    name="TextParser",
    version=__version__,
    author="Zhaohui Li, Yangzhou, Yuanzheng Wang, Yingyan Li, Yixing Fa et al.",
    author_email="lizhaohui@software.ict.ac.cn",
    description=("This project is implemented for the connection between the \
                 App layer and the base TextParser layer."),
    license="Apache 2.0",
    keywords="natural language understanding api",
    url="https://github.com/faneshion/TextParser",
    packages=find_packages(),
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        "License :: OSI Approved :: Apache Software License",
        'Programming Language :: Python :: 3.6'
    ],
    install_requires=install_requires,
    extras_require=extras_requires
)

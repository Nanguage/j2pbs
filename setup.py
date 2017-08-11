import os
from codecs import open
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

# load about information
about = {}
with open(os.path.join(here, 'j2pbs', '__version__.py'), 'r', 'utf-8') as f:
    exec(f.read(), about)

#with open('README.md', 'r', 'utf-8') as f:
#    readme = f.read()

requires = []

setup(
    name=about['__title__'],
    version=about['__version__'],
    keywords=about['__keywords__'],
    description=about['__description__'],
#    long_description=readme,
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=['j2pbs'],
    package_data={'':['LICENSE'], 'j2pbs': []},
    package_dir={'j2pbs': 'j2pbs'},
    install_requires=requires,
    license=about['__license__'],
    classifiers=(
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    )
)

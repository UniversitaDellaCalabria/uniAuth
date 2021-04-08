import re
import sys

from glob import glob
from setuptools import setup, find_packages

_src_folder = '.'
_pkg_name = 'uniauth_saml2_idp'


def readme():
    with open('README.md') as f:
        return f.read()


def get_requirements(fname='requirements.txt'):
    fopen = open(fname, 'r')
    return fopen.read().splitlines()


setup(
    name="uniauth_saml2_idp",
    version='2.0.0-alpha2',
    description="uniAuth is a Django SAML2 Identity Provider",
    long_description=readme(),
    long_description_content_type='text/markdown',
    author='Giuseppe De Marco, Francesco Filicetti',
    author_email='giuseppe.demarco@unical.it, francesco.filicetti@unical.it',
    license="Apache 2.0",
    url='https://github.com/UniversitaDellaCalabria/uniAuth',

    packages=[f"{_pkg_name}"],
    package_dir={f"{_pkg_name}": f"{_src_folder}/{_pkg_name}"},

    package_data={f"{_pkg_name}": [i.replace(f'{_src_folder}/{_pkg_name}/', '')
                                   for i in glob(f'{_src_folder}/{_pkg_name}/**',
                                                 recursive=True)]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        ],
    install_requires=get_requirements(),
    zip_safe=False,
    )

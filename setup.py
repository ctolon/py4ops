#! /usr/bin/env python

import importlib
import os
import platform
import shutil
import sys
from os.path import join
import platform

from setuptools import Command, setup, find_packages
DISTNAME = "py4ops"
DESCRIPTION = "A python Library for Automating Tasks on remote hosts."
with open("README.md") as f:
    LONG_DESCRIPTION = f.read()
MAINTAINER = "Cevat Batuhan Tolon"
MAINTAINER_EMAIL = "cevat.batuhan.tolon@cern.ch"
#URL = ""
DOWNLOAD_URL = "https://pypi.org/project/py4ops/#files"
LICENSE = "Apache 2.0"
PROJECT_URLS = {
    "Bug Tracker": "https://github.com/ctolon/py4ops/issues",
    # "Documentation": "https://www.py4ops.com",
    "Source Code": "https://github.com/ctolon/py4ops",
}
VERSION = "0.0.1"


# Custom clean command to remove build artifacts
class CleanCommand(Command):
    description = "Remove build artifacts from the source tree"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Remove c files if we are not within a sdist package
        cwd = os.path.abspath(os.path.dirname(__file__))
        remove_c_files = not os.path.exists(os.path.join(cwd, "PKG-INFO"))
        if remove_c_files:
            print("Will remove generated .c files")
        if os.path.exists("build"):
            shutil.rmtree("build")
        for dirpath, dirnames, filenames in os.walk("py4ops"):
            for filename in filenames:
                root, extension = os.path.splitext(filename)

                if extension in [".so", ".pyd", ".dll", ".pyc"]:
                    os.unlink(os.path.join(dirpath, filename))

                if remove_c_files and extension in [".c", ".cpp"]:
                    pyx_file = str.replace(filename, extension, ".pyx")
                    if os.path.exists(os.path.join(dirpath, pyx_file)):
                        os.unlink(os.path.join(dirpath, filename))

                if remove_c_files and extension == ".tp":
                    if os.path.exists(os.path.join(dirpath, root)):
                        os.unlink(os.path.join(dirpath, root))

            for dirname in dirnames:
                if dirname == "__pycache__":
                    shutil.rmtree(os.path.join(dirpath, dirname))
                    
cmdclass = {
    "clean": CleanCommand,
}

            
def setup_package():
    
    # python_requires = ">=3.6"
    # required_python_version = (3, 6)

    metadata = dict(
        name=DISTNAME,
        maintainer=MAINTAINER,
        author=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        author_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license=LICENSE,
        #url=URL,
        download_url=DOWNLOAD_URL,
        project_urls=PROJECT_URLS,
        version=VERSION,
        # package_dir={"py4ops": "py4ops"},
        keywords=["configuration management", "automation", "secure shell"],
        packages=find_packages(),
        classifiers=[
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python",
            "Topic :: Software Development",
            'Topic :: System :: Distributed Computing',
            "Topic :: Scientific/Engineering",
            "Development Status :: 4 - Beta",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX",
            "Operating System :: Unix",
            "Operating System :: MacOS",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            'Framework :: AsyncIO'
        ],
        cmdclass=cmdclass,
        # python_requires=python_requires,
        #install_requires=['paramiko>=4'],
        package_data={"": ["*.csv", "*.gz", "*.txt", "*.pxd", "*.md", "*.jpg"]},
        zip_safe=False,  # the package can run out of an .egg file
        # extras_require={"with_paramiko": ["paramiko"]}
    )
                
    setup(**metadata)

if __name__ == "__main__":
        
    setup_package()



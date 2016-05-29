#!/usr/bin/env python3
#
# build-utilities
# Copyright (c) 2015, Alexandre ACEBEDO, All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.
#
"""
Setup script for build-utilities
"""
import sys
import argparse
import shutil
import os
from platform import python_version
import site
from git import Repo
import git
try:
  from setuptools import setup, find_packages
except Exception as e:
  sys.exit("setuptools for python3 is missing")


def process_setup():
    """
    Setup function
    """
    if sys.version_info < (3,0):
        sys.exit("build-utilities only supports python3. Please run setup.py with python3.")
  
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--prefix", type=str)
    
    args = parser.parse_args(sys.argv[2:])
    if args.prefix != None:
      os.environ["PYTHONPATH"] = os.path.join(args.prefix,"lib","python{}.{}".format(python_version()[0],python_version()[2]),"site-packages")
    
    version = "0.0.0"
    print(os.path.dirname(os.path.realpath(__file__)))
    if git.repo.fun.is_git_dir(os.path.join(os.path.dirname(os.path.realpath(__file__)),".git")):
      repo = Repo(os.path.dirname(os.path.realpath(__file__)))
      for tag in repo.tags:
        if tag.commit == repo.head.commit:
          version = tag.name
          break
    
    setup(
        name="build-utilities",
        version=version,
        packages=find_packages("src"),
        package_dir ={'':'src'},
        install_requires=['argcomplete>=1.0.0','argparse>=1.0.0', 'GitPython>=2.0', 'progressbar2>=2.0.0'],
        author="Alexandre ACEBEDO",
        author_email="Alexandre ACEBEDO",
        description="Build utilities for python and go projects.",
        license="LGPLv3",
        keywords="build go python",
        url="http://github.com/aacebedo/build-utilities",
        entry_points={'console_scripts':
                      ['build-utilities = buildutilities.__main__:BuildUtilities.main']}
    )
      
if __name__ == "__main__":
    process_setup()
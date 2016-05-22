#!/usr/bin/env python3
# This file is part of build-utilities.
#
#    build-utilities is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    build-utilities is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details
#
#    You should have received a copy of the GNU General Public License
#    along with build-utilities.  If not, see <http://www.gnu.org/licenses/>.

import json
import argparse
import subprocess
import sys
import os
import uuid
import time
import shutil
from git import Repo
from platform import python_version
class TargetDesc :
  distrib = ""
  arch = ""
  package_path = ""
  
  def __init__(self,distrib,arch,package_path):
    self.distrib = distrib
    self.arch = arch
    self.package_path = package_path
  
class BuildUtilities:
  
  @staticmethod
  def parse_arguments(raw_args):
    parser = argparse.ArgumentParser(prog="build",
                                 description='Project Builder')
    rootSubparsers = parser.add_subparsers(dest="function")
    buildParser = rootSubparsers.add_parser('build', help='Build packages')
    buildParser.add_argument('--project', '-p', required=True,
                             help="Github project", type=str)
    buildParser.add_argument('--arch', '-a', required=True,
                             help='Architecture to build', type=str)
    buildParser.add_argument('--branch', '-b', help='Git branch to build',
                             default="master", type=str)
    buildParser.add_argument('--binname', '-bn', required=True,
                             help='binname', type=str)
    buildParser.add_argument('--outputdir', '-o', help='Output directory',
                        required=True, type=str)
    buildParser.add_argument('--language', '-l', help='language',
                        required=True, type=str, choices=["go","python"])
    
    pkgParser = rootSubparsers.add_parser('package', help='Packages files')
    pkgParser.add_argument('--project', '-p', required=True,
                             help="Github project", type=str)
    pkgParser.add_argument('--arch', '-a', required=True,
                             help='Architecture to build', type=str)
    pkgParser.add_argument('--branch', '-b', help='Git branch to build',
                             default="master", type=str)
    pkgParser.add_argument('--binname', '-bn', required=True,
                             help='binname', type=str)
    pkgParser.add_argument('--outputdir', '-o', help='Output directory',
                        required=True, type=str)
    pkgParser.add_argument('--inputdir', '-i', help='Input directory',
                        required=True, type=str)
   
        
    deployDescParser = rootSubparsers.add_parser('deploydesc',
                                                 help='Create bintray deployement \
                                                 descriptor')
    deployDescParser.add_argument('--project', '-p', required=True,
                             help="Github project", type=str)
    deployDescParser.add_argument('--branch', '-b', help='Git branch to build',
                             required=True, type=str)
    deployDescParser.add_argument('--binname', '-bn', required=True,
                             help='binname', type=str)
    deployDescParser.add_argument('-user', '-u', required=True,
                        help='User', type=str)
    deployDescParser.add_argument('--description', '-dc', required=True,
                        help='Package description', type=str)
    deployDescParser.add_argument('--outputpath', '-o',
                                  help='Output path',
                                  required=True, type=str)
    deployDescParser.add_argument('--packagepath', '-pa',
                                  help='Package path',
                                  required=True, type=str)
    deployDescParser.add_argument('--distrib', '-d',
                                  help='Distribution',
                                  required=True, type=str)
    deployDescParser.add_argument('--arch', '-a',
                                  help='Architecture',
                                  required=True, type=str)
    deployDescParser.add_argument('--licenses', '-li', help='Software licences',
                        default=[], type=str, action='append')
    deployDescParser.add_argument('--labels', '-la', help='Package labels',
                                  action='append',
                        default=[], type=str)
    return parser.parse_args(raw_args)
  
  @staticmethod
  def generate_tmp_dir():
    tmp_dir_path = None
    for _ in range(0, 5):
      tmp_dir_path = os.path.join(os.path.abspath(os.sep), "tmp", str(uuid.uuid4()))
      if not os.path.exists(tmp_dir_path) :
        os.makedirs(tmp_dir_path, exist_ok=True)
        break
      else:
        tmp_dir_path = None
    if tmp_dir_path == None:
      raise Exception("Unable to generate a tmp direcctory")
    return tmp_dir_path
  
  @staticmethod
  def generate_package(outputdir_path,
                      package_type, package_name, version, arch, project,path_to_package):
    res = shutil.which("fpm")
    if res is None:
      raise Exception("Packaging is not possible (fpm not found). Please install fpm (gem install fpm).")
    os.makedirs(os.path.join(outputdir_path,"packages"),exist_ok = True)
    process = subprocess.Popen(["fpm", "-t", package_type,
                                   "-n", package_name,
                                   "-p", outputdir_path,
                                   "-a", arch,
                                   "-f",
                                   "--prefix",os.path.join("usr","local"),
                                   "--url","https://www.github.com/{}".format(project),
                                   "-v", version.replace("/", "_"),
                                   "-s", "dir","."], shell=False, cwd=path_to_package)
    process.communicate()
    if process.returncode != 0:
      raise Exception("Error while cloning project")
  
  @staticmethod
  def build_python(output_dir_path, project, branch, arch, bin_name):
    if len(os.listdir(output_dir_path)) != 0:
      raise Exception("Build error: {} is not empty.".format(output_dir_path))
    
    src_dir_path = os.path.join(output_dir_path, "src")
    install_dir_path = os.path.join(output_dir_path, "install")
    
    Repo.clone_from("https://github.com/{}".format(project), src_dir_path, branch=branch)
    os.makedirs(os.path.join(install_dir_path,"lib","python{}.{}".format(python_version()[0],python_version()[2]),"site-packages"),exist_ok = True)
    process = subprocess.Popen(["python3", "./setup.py", "install", "--prefix={}".format(install_dir_path)],
                     cwd=src_dir_path, shell=False,
                     env=dict(os.environ,PYTHONPATH=os.path.join(install_dir_path,"lib","python{}.{}".format(python_version()[0],python_version()[2]),"site-packages")))
    process.communicate()
    if process.returncode != 0:
      raise Exception("Error while getting dependencies project")
  
  @staticmethod
  def build_go(output_dir_path, project, branch, arch, bin_name):
    if len(os.listdir(output_dir_path)) != 0:
      raise Exception("Build error: {} is not empty.".format(output_dir_path))
    go_dir_path = os.path.join(BuildUtilities.generate_tmp_dir(), "go")
    print("Go path is : {}".format(go_dir_path))
    src_dir_path = os.path.join(go_dir_path, 'src', "github.com", project)
    
    process = subprocess.Popen(["git", "clone", "-b", branch,
                                  "https://github.com/{}".format(project),
                                  src_dir_path], shell=False)
    process.communicate()
    if process.returncode != 0:
      raise Exception("Error while cloning project")
  
    process = subprocess.Popen(["go", "get", "-d", "./..."],
                     cwd=src_dir_path, shell=False,
                     env=dict(os.environ,
                              GOARCH=arch,
                              GOPATH=go_dir_path,
                              CGO_ENABLED="0"))
    process.communicate()
    if process.returncode != 0:
      raise Exception("Error while getting dependencies project")
  
    process = subprocess.Popen(["go", "install", "./..."],
                     cwd=src_dir_path, shell=False,
                     env=dict(os.environ,
                              GOARCH=arch,
                              GOPATH=go_dir_path,
                              CGO_ENABLED="0"))
    process.communicate()
    if process.returncode != 0:
      raise Exception("Error while build the project")
    bin_dir_path = os.path.join(output_dir_path, "packaging",
                                    "usr", "local", "bin")
    os.makedirs(bin_dir_path)
    for dirName, _, fileList in os.walk(os.path.join(go_dir_path, "bin")):
      for fname in fileList:
          shutil.copy2(os.path.join(dirName, fname),
                       os.path.join(bin_dir_path, fname))
  
    if os.path.exists(os.path.join(src_dir_path, "resources")) :
      for name in os.listdir(os.path.join(src_dir_path, "resources")):
        shutil.copytree(os.path.join(src_dir_path, "resources", name),
                        os.path.join(output_dir_path, "packaging", name))
        
  @staticmethod
  def generate_bintray_descriptor(output_path,
                                project,
                                bin_name,
                                user,
                                desc,
                                version,
                                targets,
                                licenses=[],
                                labels=[]):
    if os.path.exists(output_path) :
      raise Exception("File {} exists".format(output_path))
    github_addr = "https://github.com/{}".format(project)
    descriptor = {"package":{
                             "name":bin_name,
                             "repo":bin_name,
                             "subject":user,
                             "desc":desc,
                             "website_url":github_addr,
                             "issue_tracker_url":github_addr,
                             "vcs_url":github_addr,
                             "github_use_tag_release_notes":True,
                             "licenses":licenses,
                             "labels":labels,
                             "public_download_numebrs":False,
                             "public_stats":False
                             },
                  "version":{
                             "name":version,
                             "desc":desc,
                             "released":time.strftime("%Y-%m-%d"),
                             "vcs_tag":version,
                             "gpgSign":False
                             },
                  "files":[],
                  "publish":True
                  }
    
    for t in targets: 
      if os.path.isfile(t.package_path):
        descriptor["files"].append({
                        "includePattern": t.package_path,
                        "uploadPattern": os.path.join(t.distrib,"$1"),
                        "matrixParams":
                          {
                            "deb_distribution":t.distrib,
                            "deb_component":"main",
                            "deb_architecture":t.arch
                           }
                       })
    outfile = open(output_path, 'w')
    json.dump(descriptor, outfile, ensure_ascii=False, indent=2)
    outfile.close()

  @staticmethod
  def main():
    try:
      args = BuildUtilities.parse_arguments(sys.argv[1:])
      
      if args.function == "build" :
        if not os.path.exists(args.outputdir):
          os.makedirs(args.outputdir, exist_ok=True)
        if args.language == "python":
          BuildUtilities.build_python(args.outputdir,
            args.project, args.branch,
            args.arch, args.binname)
        elif args.language == "go":
          BuildUtilities.build_go(args.outputdir,
            args.project, args.branch,
            args.arch, args.binname)
        else:
          raise Exception("Invalid language {}".format(args.language))
        
      if args.function == "package" :
        if not os.path.exists(args.outputdir):
          os.makedirs(args.outputdir, exist_ok=True)
        BuildUtilities.generate_package(args.outputdir, "deb", args.binname,
                      args.branch, args.arch, args.project,args.inputdir)
        BuildUtilities.generate_package(args.outputdir, "tar", args.binname,
                      args.branch, args.arch, args.project,args.inputdir)
      elif args.function == "deploydesc" :
        t = TargetDesc(args.arch, args.distrib, args.packagepath)
        BuildUtilities.generate_bintray_descriptor(args.outputpath,args.project,
                                  args.binname,
                                  args.user,
                                  args.description,
                                  args.branch,
                                  [t],
                                  args.licenses,
                                  args.labels)
      sys.exit(0)
    except Exception as e:
      sys.exit(str(e))

    
if __name__ == "__main__":
  BuildUtilities.main()
# DEPRECATED -- the functionality of this script should now be performed by setup_new_proj.py in the root dir
#
# Copy the relevant files and subdirs from your PhysiCell project to this directory
# Usage:
#   python copy_myproj.py </full/path/to/PhysiCell-proj>
#   e.g.,
#   python copy_myproj.py /Users/heiland/dev/PhysiCell-biorobots

import sys
import os
import shutil

num_args = len(sys.argv)
print('num_args=',num_args)
if (num_args < 2):
    print("Usage: %s </full/path/to/PhysiCell-proj>")
    sys.exit(1)
path_to_proj = sys.argv[1]
print('path_to_proj=',path_to_proj)

#shutil.copytree('/Users/heiland/dev/PhysiCell_V1.4.1-b/core','./core')
dir_names = ["core", "BioFVM", "modules", "custom_modules"]
for dname in dir_names:
  from_dir = os.path.join(path_to_proj, dname)
  to_dir = os.path.join(".", dname)
  print(from_dir, " --> ", to_dir)
  shutil.copytree(from_dir, to_dir)

from_file = os.path.join(path_to_proj, "Makefile")
to_file = os.path.join(".", "Makefile")
print(from_file, " --> ", to_file)
shutil.copy(from_file, to_file)

from_file = os.path.join(path_to_proj, "main.cpp")
to_file = os.path.join(".", "main.cpp")
print(from_file, " --> ", to_file)
shutil.copy(from_file, to_file)

from_file = os.path.join(path_to_proj, "VERSION.txt")
to_file = os.path.join(".", "VERSION.txt")
print(from_file, " --> ", to_file)
shutil.copy(from_file, to_file)


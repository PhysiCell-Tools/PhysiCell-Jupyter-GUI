# 
# setup_new_proj.py - create a new PhysiCell Jupyter notebook project [for nanoHUB] by copying the contents of this 
#                     project and an existing PhysiCell project into the new project.
#
# Assumptions:
#   - the new project is a cloned, empty, public GitHub repo
#   - you have an existing PhysiCell project with files in specified locations: 
#       - config/PhysiCell_settings.xml 
#       - output/initial.xml)
# 
# Usage:
#   python setup_new_proj.py  <full-path-to-new-project>  <simple-project-name>  <full-path-to-PhysiCell-project>
#  e.g.:
#   python setup_new_proj.py  /Users/heiland/git/iu399_proj1  iu399_proj1  /Users/heiland/dev/PhysiCell_heterogeneity
#

import sys
import shutil
import os
import platform


num_args = len(sys.argv)
print('num_args=',num_args)
if (num_args < 3):
#    print("Usage: %s <full-path-to-new-project>  <simple-project-name>  <full-path-to-PhysiCell-project>")
    print("Usage: %s <full-path-to-new-project>  <full-path-to-PhysiCell-project>")
#    print("Usage: %s <your repo name>")
    sys.exit(1)
#print('sys.argv[0] = ',sys.argv[0])
proj_fullpath = sys.argv[1]
print('proj_fullpath = ',proj_fullpath)

#proj_name = sys.argv[2]
proj_name = os.path.basename(proj_fullpath)
print('proj_name = ',proj_name)

physicell_fullpath= sys.argv[2]
print('physicell_fullpath = ',physicell_fullpath)

print("\n STEP 1: copy tool4nanobio to new project:\n")
for elm in os.listdir('.'):
    try:
        if (elm[0] != '.'):  # avoid /.git, etc
            if os.path.isdir(elm):
                from_dir = elm
                to_dir = os.path.join(proj_fullpath, elm)
                print(from_dir, " --> ", to_dir)
                # shutil.copytree(elm, os.path.join(proj_fullpath, elm))        # (from_dir, to_dir)
                shutil.copytree(from_dir, to_dir)
            else:
                if (elm == sys.argv[0] or elm == "README.md"):
                    # print('------- skipping over ',elm)
                    continue
                from_file = elm
                to_file = os.path.join(proj_fullpath, elm)        # (from_file, to_file)
                print(from_file, " --> ", to_file)
                shutil.copy(from_file, to_file)
    except:
#        print("   can't copy ",elm," to ", proj_fullpath, " ... maybe you already did?")
        print("   can't copy ... maybe you already did?")

#------------------------------------
print("\n\n STEP 2: copy PhysiCell project's source (and data files) to new project's /src:\n")
# Copy (most of) your PhysiCell project to your project's /src directory
#os.chdir(os.path.join(proj_fullpath, 'src'))
proj_src_dir = os.path.join(proj_fullpath, 'src')
print("proj_src_dir = ",proj_src_dir)

dir_names = ["core", "BioFVM", "modules", "custom_modules"]
for dname in dir_names:
    from_dir = os.path.join(physicell_fullpath, dname)
    to_dir = os.path.join(proj_src_dir, dname)
    print(from_dir, " --> ", to_dir)
    try:
        shutil.copytree(from_dir, to_dir)
    except:
        print("   can't copy ... maybe you already did?")

from_file = os.path.join(physicell_fullpath, "Makefile")
to_file = os.path.join(proj_src_dir, "Makefile")
print(from_file, " --> ", to_file)
shutil.copy(from_file, to_file)

from_file = os.path.join(physicell_fullpath, "main.cpp")
to_file = os.path.join(proj_src_dir, "main.cpp")
print(from_file, " --> ", to_file)
shutil.copy(from_file, to_file)

from_file = os.path.join(physicell_fullpath, "VERSION.txt")
to_file = os.path.join(proj_src_dir, "VERSION.txt")
print(from_file, " --> ", to_file)
shutil.copy(from_file, to_file)

from_file = os.path.join(physicell_fullpath, "config", "PhysiCell_settings.xml")
to_file = os.path.join(proj_fullpath, "data", "PhysiCell_settings.xml")
print(from_file, " --> ", to_file)
shutil.copy(from_file, to_file)

print("   Editing ", to_file, ": <folder>output</folder> --> <folder>.</folder>")
with open(to_file, 'r') as myfile:
    new_text = myfile.read().replace('output', ".")
with open(to_file, 'w') as myfile:
    myfile.write(new_text)

from_file = os.path.join(physicell_fullpath, "output", "initial.xml")
to_file = os.path.join(proj_fullpath, "data", "initial.xml")
print(from_file, " --> ", to_file)
shutil.copy(from_file, to_file)

#------------------------------------


sys.exit(1)


# NOTE: let's not do this now; rather edit the invoke script *on* github to avoid 
#       the (Windows) problem of making it a non-executable file
#with open('middleware/invoke', 'r') as myfile:
#    new_text = myfile.read().replace('tool4nanobio', gui_name)
#with open('middleware/invoke', 'w') as myfile:
#    myfile.write(new_text)

#--------------
old_file = os.path.join("bin", 'tool4nanobio.py')
new_file = os.path.join("bin", gui_name + '.py')
try:
    shutil.move(old_file, new_file)
    print('Renaming ',old_file, ' to ',new_file)
except:
    print("  ---> Cannot rename ",old_file," to ",new_file, ", but we will continue")

print('Replacing gui_name in ',new_file)
with open(new_file, 'r') as myfile:
    new_text = myfile.read().replace('tool4nanobio', gui_name)
with open(new_file, 'w') as myfile:
    myfile.write(new_text)

#--------------
old_file = 'tool4nanobio.ipynb'
new_file = gui_name + '.ipynb'
try:
    shutil.move(old_file, new_file)
    print('Renaming ',old_file, ' to ',new_file)
except:
    print("  ---> Cannot rename ",old_file," to ",new_file, ", but we will continue")

print('Replacing gui_name in ',new_file)
with open(new_file, 'r') as myfile:
    new_text = myfile.read().replace('tool4nanobio', gui_name)
with open(new_file, 'w') as myfile:
    myfile.write(new_text)


#--------------
"""
In /data:
python xml2jupyter.py PhysiCell_settings.xml
Copy the generated user_params.py to ../bin
"""
print('Trying to run xml2jupyter.py on your .xml file in /data')
os.chdir("data")
cmd = "python xml2jupyter.py PhysiCell_settings.xml"
try:
    os.system("python xml2jupyter.py PhysiCell_settings.xml")
except:
    print("  ---> Cannot execute: ",cmd)


new_file = os.path.join("..","bin")
try:
    shutil.copy("user_params.py", new_file)
except:
    print("  ---> Cannot copy data/user_params.py to bin/user_params.py")
    print("         You will need to do that manually.\n")

if platform.system() != 'Windows':
    try:
        print("Trying to import hublib.ui")
        import hublib.ui
    except:
        print("hublib.ui is not found, will try to install it.")
        os.system("pip install -U hublib")

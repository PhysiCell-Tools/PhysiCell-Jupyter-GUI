# PhysiCell-Jupyter-GUI
This repository helps auto-generate a Jupyter notebook GUI for PhysiCell-related models and output. The directory structure and content of the repository matches a template required for a [nanoHUB](https://nanohub.org/) tool installation. However, creating an actual nanoHUB tool is optional; the GUI created here should also work (with fewer bells & whistles, perhaps) on your personal computer, assuming you have the required Python modules and are able to run a Jupyter notebook server.

It also contains a directory of an example GUI that has been generated using this process (although it may not reflect the very latest version of the GUI). See `Example_GUIs`.
So, after cloning this repo, you should be able to at least run an example notebook and see the GUI, even though
you won't be able to 'Run' a simulation since that would require compiling the code (the PhysiCell model)
and copying certain files to appropriate locations, as described below. To run an example notebook:
```
#---- clone this repo, then from a shell window:
$ cd Example_GUIs/pc4biorobots
$ jupyter notebook pc4biorobots.ipynb
```


## Dependencies/Requirements
* We highly recommend installing the [Anaconda Python 3.x](https://www.anaconda.com/distribution) distribution. This will contain Python and various 3rd party modules needed to create the PhysiCell Jupyter notebook (PhysiCell GUI). It will also contain the Jupyter notebook server to test the GUI.
* You need to be able to run Anaconda's 'python' from the command line. You can 1) edit your PATH system variable, 2) provide the full path command, or 3) create an alias.
* If you are not on Windows, it may be possible to install a Python module (hublib) that will provide customized widgets for the GUI. (The make_my_tool.py script will attempt to install this on OSX or Linux, not Windows)
* You have PhysiCell installed, have an example model compiled, and have successfully run it. The script below assumes you have: ```Makefile, main.cpp, config/PhysiCell_settings.xml, and output/initial.xml``` files in your PhysiCell directory. (If you do not, certain aspects of this automated process will fail and you'll need to manually create and/or copy files)
* the directory where you cloned your "project repo" (next section) is essentially empty (it might contain a README.md)

## Steps to follow

1. Create a new, public repository on github.com (not the IU github) and clone it to your computer. This will be your "project repo". Call it whatever you want (it doesn't have to match the name of your eventual nanoHUB tool). If you create a README.md, make a backup copy in case it gets overwritten in the steps below. For the example steps below, we choose the name "ise_proj1".
2. Clone this repo to your computer.
3. In a command line shell window (terminal or command prompt), from the root directory of this repo, run the Python script called ```setup_new_proj.py```. If successful, this will copy (nearly) all necessary files into your new project repo (step 1). You provide three required arguments (and two optional) to the script:
```
<full-path-to-new-project>  <full-path-to-PhysiCell-project>  <tool name>  [<makefile name>  <main cpp>]
```
The default names of the optional arguments will simply be "Makefile" and "main.cpp".

Variations of running the script might be - from a Unix-like shell:
```
$ python setup_new_proj.py  /Users/heiland/git/ise_proj1  /Users/heiland/dev/PhysiCell_heterogeneity iu399sp19p099
$ python setup_new_proj.py  ~/git/ise_proj1  ~/dev/PhysiCell_heterogeneity iu399sp19p099

$ python setup_new_proj.py  ~/git/ise_proj1  ~/dev/PhysiCell_heterogeneity iu399sp19p099 Make_hetero main_hetero.cpp

[Windows Git Bash] MINGW64
$ python setup_new_proj.py  /c/Users/heiland/git/ise_proj1  /c/Users/heiland/dev/PhysiCell_heterogeneity iu399sp19p099
$ python setup_new_proj.py  ~/git/ise_proj1  ~/dev/PhysiCell_heterogeneity iu399sp19p099
```
from a Windows Command Prompt or PowerShell:
```
>python setup_new_proj.py  C:\Users\heiland\git\ise_proj1  C:\Users\heiland\dev\PhysiCell_heterogeneity iu399sp19p099
```
<!--
4. From your root directory of your new project repo, run ```make_my_tool.py```, for example:
```
~/git/ise_proj1$ python make_my_tool.py ise_proj1
```
5. Edit the Makefile in the /src directory so the compiled program will be called ```myproj```:
```
PROGRAM_NAME := myproj
```
-->
4. Build your PhysiCell project in your /src directory and copy the resulting ```myproj``` executable to ../bin:
```
(bash commands)
~/git/ise_proj1$ cd src
~/git/ise_proj1/src$ make
...
~/git/ise_proj1/src$ cp myproj ../bin      # will be "myproj.exe" on Windows
~/git/ise_proj1$ cd ..
```

5. Try to display the new Jupyter notebook:
```
~/git/ise_proj1$ jupyter notebook ise_proj1.ipynb
```

Select ‘Cell’ → ‘Run All’ menu item to display the notebook (or, if necessary, select the 'Kernel' → ‘Restart & Run All’ menu item).
Click the ‘Run’ button in the GUI to see if it works. Output files should appear in the ```tmpdir``` sub-directory.

6. If it's successful, commit everything to the GitHub repo for your new project.
7. Perform steps to create your nanoHUB tool (optional) - see section below.

<!--
If everything appears to be correct and you want to test and possibly publish your tool on nanoHUB:
* Delete tool4nanobio.zip in your repo. Optionally, clean up (delete) /src/*.o
* Commit files to your GitHub repo.
-->


## Create a nanoHUB tool (optional)

* If you do not have a nanoHUB account, register for one at https://nanohub.org/register/
* Students need to be aware that creating an account on nanoHUB is similar to creating an account on any social media platform. Use your good judgment about publicly sharing personal information. For more background, see https://ferpa.iu.edu/safeguarding/index.html
* On https://nanohub.org/tools/create, fill out the basic information for creating your nanoHUB tool. Tool Name should be 3-15 alphanumeric characters, including at least one non numeric character (e.g., ```iu399sp19p099```). Although not required, it’s probably wise to also use only lowercase characters. Provide the URL to your newly created GitHub repo (e.g., ```https://github.com/...```) and also select the bullet to ```Publish as a Jupyter notebook```. When you finally click the ```Register Tool``` button, you will be told if that tool name has already been taken, however, it may take a few seconds for that to appear. Also, don't worry if you forget to provide some info on this initial form, you can always edit it later.

<!--
* In another tab of your browser, go to your newly created repository and edit the ```middleware/invoke``` script *in-place*. You want the name of the .ipynb to be your newly created notebook (=repo) name and the name following the ```-t``` to be the name of your nanoHUB tool. For example:
```
/usr/bin/invoke_app "$@" -C "start_jupyter -A -T @tool ise_proj1.ipynb" -t iu399sp19p099 \
```
If you happened to create your repo to be the same name as your nanoHUB tool, then it would be:
```
/usr/bin/invoke_app "$@" -C "start_jupyter -A -T @tool iu399sp19p099.ipynb" -t iu399sp19p099 \
```
The reason we edit this file in-place is to retain its executable mode. It should be indicated as follows:
-->

Before you request to have your tool installed on nanoHUB, you need to make sure the ```invoke``` file in the ```middleware``` subdirectory is executable:

![alt ensure executable](https://github.com/rheiland/tool4nanobio/blob/master/doc/invoke_file_exec_mode.png)

If you are using Windows, this file seems to lose its "executable" permission when you commit it. You will need to ```cd``` into the ```middleware``` folder of your newly created project and, using ```git``` from the command line:
```
$ git update-index --chmod=+x invoke
$ git commit -m "Changing file permissions"
$ git push
```
then view/refresh the ```invoke``` file from your browser and verify "Executable File" appears in the upper-left as in the screenshot above.

* From the status page of your new tool on nanoHUB (e.g., https://nanohub.org/tools/iu399sp19p099/status), click the link to have it installed for testing (below the "We are waiting for You"). (You must be logged in to nanoHUB). Wait "1-3 days" for that to happen (typically, it's usually within minutes or hours). You'll receive an email from nanoHUB when the tool is installed.

The following is a screenshot of a nanoHUB tool's status page:
![alt tool status page](https://github.com/rheiland/tool4nanobio/blob/master/doc/nanohub_tool_status_page-med.png)

* After your tool in installed and you have tested it and feel like it’s ready to publish, click the link on your tool’s status page that you approve it (for publishing). But as the above screenshot says, you will first need to create a description of your tool. You will eventually be asked to provide the license for your tool and check a box to verify the license is indeed correct. You'll receive an automated email from nanoHUB saying the tool status changed from "Created to Uploaded". The nanoHUB sys admin will then need to compile your code and deploy it there. You will receive another email when the tool is ready to test on nanoHUB.

## Details of the above scripts (if you care)

In more detail, the ```setup_new_proj.py``` script should:

* Copy the contents of the tool4nanobio repo to your newly created repo (but NOT the hidden ```.git``` directory!)

* Copy the relevant files from your PhysiCell model into the new repo's /src directory. Basically, you need to get all of your PhysiCell code (and directory structure) into /src so that when you type ```make``` there, it will build your project. For example, one would typically do: <!-- the following (there's a Python script in /src called ```copy_myproj.py``` that should perform these copies - see Example Steps below): -->

        * copy all /core/ files into the /src/core/ directory   
        * copy all /BioFVM/ files into the /src/BioFVM/ directory
        * copy all /modules/ files into the /src/modules/ directory
        * copy all /custom_modules/ files into the /src/custom_modules/ directory
        * copy your main.cpp into /src
        * copy your Makefile into src/Makefile and 
     
The src/Makefile needs to be edited so that:
```
PROGRAM_NAME := myproj

osRelease = $(shell lsb_release -r | sed -e "s/Release:\W*//" -e "s/\..*//")
ifeq ($(osRelease),7)
   hostName = $(shell hostname | sed -e "s:[-_].*::")$(osRelease)
else
   hostName = $(shell hostname | sed -e "s:[-_].*::")
endif
ifeq ($(hostName),nanohub7)
   BIN = ../bin
   MODINIT = . /etc/environ.sh
   MODCMD = use -e -r anaconda3-5.1
else
ifeq ($(hostName),rice7)
   BIN = ../bin/rice7
   MODINIT = . $(MODULESHOME)/init/sh
   MODCMD = module purge 2> /dev/null; module load gcc/7.3.0
endif
ifeq ($(hostName),brown7)
   BIN = ../bin/brown7
   MODINIT = . $(MODULESHOME)/init/sh
   MODCMD = module purge 2> /dev/null; module load gcc/7.3.0
endif
endif
```
and in the `all` target, comment out copying the executable to ../bin:
```
all: main.cpp $(ALL_OBJECTS)
	$(COMPILE_COMMAND) -o $(PROGRAM_NAME) $(ALL_OBJECTS) main.cpp 
#	cp $(PROGRAM_NAME) ../bin
```
also, be sure it has the following targets present (with the necessary leading tabs):
```
install:
	$(MODINIT); $(MODCMD);  make all
	install --mode 0755 -D $(PROGRAM_NAME) $(BIN)/$(PROGRAM_NAME)

distclean: clean
	rm -f $(BIN)/$(PROGRAM_NAME)
	rm -rf $(BIN)/__pycache__
	rm -rf ../.ipynb_checkpoints
```
and this target should not have the trailing "*":
```
clean:
        rm -f *.o
#       rm -f $(PROGRAM_NAME)*
        rm -f $(PROGRAM_NAME)
```
Build using the Makefile (run ```make```) - it should build a ‘myproj’ executable. 
* copy ‘myproj’ to /bin in your repo.

* copy your .xml configuration file into data/PhysiCell_settings.xml (overwrite the one there)
* edit data/PhysiCell_settings.xml so that:
```<folder>.</folder>```

From the root dir of your repo:
* run “python make_my_tool.py <your repo name>”, 
e.g., “python make_my_tool.py ise_proj1"    <!-- iu399sp19p001” -->
  
This script will do a number of things: 
* rename two files: <!-- in the /middleware/invoke bash script, and --> the name of the notebook (```.ipynb```, in the root directory) and the primary Python module (in /bin).
* run the xml2jupyter.py script on data/PhysiCell_settings.xml and copy the resulting user_params.py and microenv_params.py into the /bin directory.
* attempt to install the “hublib” Python module that provides the fancy “Run” button widget (with Output and Cancel features).

Copy the “initial.xml”, from the output you generated when you ran your project in its original location, into this repo's /data directory.


<!--
## More verbosely (this needs to be revised)

Here is an example walk-through using commands in a (Unix-like) shell
```
~/git$ git clone git@github.com:rheiland/ise_proj1.git
Cloning into 'ise_proj1'...
warning: You appear to have cloned an empty repository.
~/git$ cd ise_proj1/

~/git/ise_proj1$ cp -R ~/git/tool4nanobio/* .

~/git/ise_proj1$ ls
LICENSE.txt		doc/			rappture/
README.md		examples/		src/
bin/			make_my_tool.py		tmpdir/
data/			middleware/		tool4nanobio.ipynb

~/git/ise_proj1$ cd src
~/git/ise_proj1/src$ ls
copy_myproj.py
~/git/ise_proj1/src$ python copy_myproj.py 
num_args= 1
Usage: %s </full/path/to/PhysiCell-proj>

~/git/ise_proj1/src$ python copy_myproj.py ~/dev/PhysiCell_heterogeneity
num_args= 2
path_to_proj= /Users/heiland/dev/PhysiCell_heterogeneity
/Users/heiland/dev/PhysiCell_heterogeneity/core  --  ./core
/Users/heiland/dev/PhysiCell_heterogeneity/BioFVM  --  ./BioFVM
/Users/heiland/dev/PhysiCell_heterogeneity/modules  --  ./modules
/Users/heiland/dev/PhysiCell_heterogeneity/custom_modules  --  ./custom_modules
/Users/heiland/dev/PhysiCell_heterogeneity/Makefile  --  ./Makefile
/Users/heiland/dev/PhysiCell_heterogeneity/main.cpp  --  ./main.cpp
/Users/heiland/dev/PhysiCell_heterogeneity/VERSION.txt  --  ./VERSION.txt


# edit the Makefile:  PROGRAM_NAME := myproj

~/git/ise_proj1/src$ 
~/git/ise_proj1/src$ ls
BioFVM/		copy_myproj.py	custom_modules/	modules/
Makefile	core/		main.cpp

~/git/ise_proj1/src$ make
 ... (will hopefully build and generate myproj)
 
 ~/git/ise_proj1/src$ cp myproj ../bin

~/git/ise_proj1/src$ cd ../data
~/git/ise_proj1/data$ ls
mygui.py	xml2jupyter.py
~/git/ise_proj1/data$ cp ~/dev/PhysiCell_heterogeneity/config/PhysiCell_settings.xml .

# edit this PhysiCell_settings.xml so that: <folder>.</folder>

~/git/ise_proj1/data$ cp ~/dev/PhysiCell_heterogeneity/output/initial.xml . 

~/git/ise_proj1/src$ cd ..
~/git/ise_proj1$ python make_my_tool.py 
num_args= 1
Usage: %s <your repo name>
 
~/git/ise_proj1$ python make_my_tool.py ise_proj1
num_args= 2
toolname= ise_proj1
Renaming  bin/tool4nanobio.py  to  bin/ise_proj1.py
Replacing toolname in  bin/ise_proj1.py
Renaming  tool4nanobio.ipynb  to  ise_proj1.ipynb
Replacing toolname in  ise_proj1.ipynb
Trying to run xml2jupyter.py on your .xml file in /data
num_args= 2
tumor_radius {'type': 'double', 'units': 'micron'}
double:  250.0 , delta_val= 10
oncoprotein_mean {'type': 'double', 'units': 'dimensionless'}
double:  1.0 , delta_val= 0.1
oncoprotein_sd {'type': 'double', 'units': 'dimensionless'}
double:  0.25 , delta_val= 0.01
oncoprotein_min {'type': 'double', 'units': 'dimensionless'}
double:  0.0 , delta_val= 0.01
oncoprotein_max {'type': 'double', 'units': 'dimensionless'}
double:  2.0 , delta_val= 0.1
random_seed {'type': 'int', 'units': 'dimensionless'}
int:  0 , delta_val= 1

 --------------------------------- 
Generated a new:  user_params.py

Trying to import hublib.ui
<IPython.core.display.Javascript object>
```

Finally, try to run the notebook to display the GUI:
```
~/git/ise_proj1$ jupyter notebook ise_proj1.ipynb 
...


If your notebook tells you a file is not found, but it's really there, e.g.:
FileNotFoundError: [Errno 2] No such file or directory: '/Users/heiland/git/ise_proj1/data/PhysiCell_settings.xml'

try the menu: Kernel -- Restart & Run All
```

If it seems to run OK, commit your code:
```
~/git/ise_proj1$ git add .
~/git/ise_proj1$ git commit -m "initial commit"
...
~/git/ise_proj1$ git push
```
-->

<!--
In the `data` directory, you will run the `xml2jupyter.py` script on the .xml file to 
generate `user_params.py`.
-->



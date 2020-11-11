"""
====================================================================================================
  Parse a PhysiCell configuration file (XML) and generate two Jupyter (Python) modules: 
    user_params.py - containing widgets for user parameters.
    microenv_params.py - containing widgets for microenvironment parameters.
  
====================================================================================================
 
  Inputs - takes none, 1, 2, 3, or 4 arguments
  ------
    config filename (str, optional): the PhysiCell configuration file (.xml) (Default = config.xml)
    GUI module (str, optional):      the primary GUI for the Jupyter notebook 
    colorname1, colorname2 (str, optional): the colors to use for the alternating rows of widgets 
                                            (Defaults: lightgreen, tan)
  Examples (with 0,1,2,3,4 args):
  --------
    python xml2jupyter.py
    python xml2jupyter.py config_heterogeneity.xml
    python xml2jupyter.py config_heterogeneity.xml mygui.py
    python xml2jupyter.py config_biorobots.xml lightblue tan
    python xml2jupyter.py config_biorobots.xml mygui.py lightblue tan
  
  Outputs
  -------
    user_params.py: Python module used to create/edit custom user parameters (--> "User Params" GUI tab)
    microenv_params.py: Python module used to create/edit custom user parameters (--> "User Params" GUI tab)
 
Authors:
Randy Heiland (heiland@iu.edu)
Daniel Mishler, Tyler Zhang, Eric Bower (undergrad students in Intelligent Systems Engineering, IU)
Dr. Paul Macklin (macklinp@iu.edu)

--- History ---
v2 - also generate the microenv_params.py
v1 - generate the user_params.py
"""

import sys
import os
import math
import xml.etree.ElementTree as ET

# Defaults
config_file = "config.xml"
colorname1 = 'lightgreen'
colorname2 = 'tan'
# bv_widget_names = []

num_args = len(sys.argv)
print("num_args=",num_args)
if (num_args < 2):
    print()
    print("*** NOTE:  using config.xml  ***")
    print()
else:
    config_file = sys.argv[1]
    if not os.path.isfile(config_file):
        print(config_file, "does not exist")
        print("Usage: python " + sys.argv[0] + " <config-file.xml> [<gui-file.py>] [<colorname1> <colorname2>]")
        sys.exit(1)

if (num_args == 3):
    gui_file = sys.argv[2]
elif (num_args == 4):
    colorname1 = sys.argv[2]
    colorname2 = sys.argv[3]
elif (num_args == 5):
    gui_file = sys.argv[2]
    colorname1 = sys.argv[3]
    colorname2 = sys.argv[4]
elif (num_args > 5):
    print("Usage: python " + sys.argv[0] + " <config-file.xml> [<gui-file.py>] [<colorname1> <colorname2>]")
    sys.exit(1)

print()
print("config_file = ",config_file)
print("colorname1 = ",colorname1)
print("colorname2 = ",colorname2)
print()

if (num_args == 3):
    with open(gui_file) as f:   # e.g., "mygui.py"
    #  newText = f.read().replace('myconfig.xml', config_file) # rwh todo: don't assume this string; find line
        file_str = f.read()
        idx = file_str.find('main_xml_filename')  # verify > -1
        file_pre = file_str[:idx] 
        idx2 = file_str[idx:].find('\n')
        file_post = file_str[idx+idx2:] 

    with open(gui_file, "w") as f:
        f.write(file_pre)
        f.write("main_xml_filename = '" + config_file + "'")
        f.write(file_post)

#---------------------------------------------------------------------------------------------------
user_tab_header = """ 
# This file is auto-generated from a Python script that parses a PhysiCell configuration (.xml) file.
#
# Edit at your own risk.
#
import os
from ipywidgets import Label,Text,Checkbox,Button,HBox,VBox,FloatText,IntText,BoundedIntText,BoundedFloatText,Layout,Box
    
class UserTab(object):

    def __init__(self):
        
        micron_units = Label('micron')   # use "option m" (Mac, for micro symbol)

        constWidth = '180px'
        tab_height = '500px'
        stepsize = 10

        #style = {'description_width': '250px'}
        style = {'description_width': '25%'}
        layout = {'width': '400px'}

        name_button_layout={'width':'25%'}
        widget_layout = {'width': '15%'}
        widget2_layout = {'width': '10%'}
        units_button_layout ={'width':'15%'}
        desc_button_layout={'width':'45%'}
        divider_button_layout={'width':'40%'}
"""

"""
        self.therapy_activation_time = BoundedFloatText(
            min=0.,
            max=100000000,
            step=stepsize,
            description='therapy_activation_time',
            style=style, layout=layout,
            # layout=Layout(width=constWidth),
        )
        self.save_interval_after_therapy_start = BoundedFloatText(
            min=0.,
            max=100000000,
            step=stepsize,
            description='save_interval_after_therapy_start',
            style=style, layout=layout,
        )

        label_blankline = Label('')

        self.tab = VBox([HBox([self.therapy_activation_time, Label('min')]), 
                         HBox([self.save_interval_after_therapy_start, Label('min')]), 
                         ])  
"""

fill_gui_str= """

    # Populate the GUI widgets with values from the XML
    def fill_gui(self, xml_root):
        uep = xml_root.find('.//microenvironment_setup')  # find unique entry point
        vp = []   # pointers to <variable> nodes
        if uep:
            for var in uep.findall('variable'):
                vp.append(var)

"""

fill_xml_str= """

    # Read values from the GUI widgets to enable editing XML
    def fill_xml(self, xml_root):
        uep = xml_root.find('.//microenvironment_setup')  # find unique entry point
        vp = []   # pointers to <variable> nodes
        if uep:
            for var in uep.findall('variable'):
                vp.append(var)

"""
def get_float_stepsize(val_str):
    # fval_abs = abs(float(ppchild.text))
    fval_abs = abs(float(val_str))
    if (fval_abs > 0.0):
        if (fval_abs > 1.0):  # crop
            delta_val = pow(10, int(math.log10(abs(float(ppchild.text)))) - 1)
        else:   # round
            delta_val = pow(10, round(math.log10(abs(float(ppchild.text)))) - 1)
    else:
        delta_val = 0.01  # if initial value=0.0, we're totally guessing at what a good delta is
    return delta_val

# Now parse a configuration file (.xml) and map the user parameters into GUI widgets
#tree = ET.parse('../config/PhysiCell_settings.xml')
try:
    tree = ET.parse(config_file)
except:
    print("Cannot parse",config_file, "- check it's XML syntax.")
    sys.exit(1)

root = tree.getroot()

indent = "        "
indent2 = "          "
widgets = {"double":"FloatText", "int":"IntText", "bool":"Checkbox", "string":"Text", "divider":""}
#widgets = {"double":"FloatText", "int":"IntText", "bool":"Checkbox", "string":"Text"}
type_cast = {"double":"float", "int":"int", "bool":"bool", "string":"", "divider":"Text"}
vbox_str = "\n" + indent + "self.tab = VBox([\n"
#param_desc_buttons_str = "\n" 
#name_buttons_str = "\n" 
units_buttons_str = "\n" 
desc_buttons_str = "\n"
header_buttons_str = "\n"
row_str = "\n"
box_str = "\n" + indent + "box_layout = Layout(display='flex', flex_flow='row', align_items='stretch', width='100%')\n"
row_header_str = "\n"
box_header_str = "\n"
#        box1 = Box(children=row1, layout=box_layout)\n"

menv_var_count = 0   # micronenv 
param_count = 0
divider_count = 0
color_count = 0
#param_desc_count = 0
name_count = 0
units_count = 0

#---------- custom user_parameters --------------------
# TODO: cast attributes to lower case before doing equality tests; perform more testing!

uep = root.find('.//user_parameters')  # find unique entry point (uep) to user params
fill_gui_str += indent + "uep = xml_root.find('.//user_parameters')  # find unique entry point\n"
fill_xml_str += indent + "uep = xml_root.find('.//user_parameters')  # find unique entry point\n"

# param_count = 0
   #param_desc_count = 0
# name_count = 0
# units_count = 0

print_vars = True
print_var_types = False

tag_list = []

# function to process a "divider" type element
def handle_divider(child):
    global divider_count, user_tab_header, indent, indent2, vbox_str
    divider_count += 1
    print('-----------> handler_divider: ',divider_count)
    row_name = "div_row" + str(divider_count)
    user_tab_header += "\n" + indent + row_name + " = " + "Button(description='" + child.attrib['description'] + "', disabled=True, layout=divider_button_layout)\n"
    vbox_str += indent2 + row_name + ",\n"


#===========  main loop ===================
# NOTE: we assume a simple "children-only" hierarchy in <user_parameters>
for child in uep:   # uep = "unique entry point" for <user_parameters> (from above)
    if print_vars:
        print(child.tag, child.attrib)

    divider_flag = False
    if child.attrib['type'].lower() == 'divider':
        divider_flag = True
    else:
        param_count += 1

    # we allow the divider elements to have the same name, but not other elements
    if (child.tag in tag_list) and (not divider_flag):
        print("-------> Warning: duplicate tag!  ", child.tag)
        continue
    else:
        tag_list.append(child.tag)
    units_str = ""
    describe_str = ""
    if 'hidden' in child.attrib.keys() and (child.attrib['hidden'].lower() == "true"):   # do we want to hide this from the user?
        print("  HIDE this parameter from the GUI: ", child.tag)
        continue

#    names_str = ''
#    units_str = ''
    # describe_str = ''
#    desc_row_name = None
    desc_row_name = ''
    units_btn_name = ''


    if not divider_flag:
        if 'description' in child.attrib.keys():
            describe_str = child.attrib['description']
        else:
            describe_str = ""
        desc_row_name = "desc_button" + str(param_count)
        desc_buttons_str += indent + desc_row_name + " = " + "Button(description='" + describe_str + "' , tooltip='" + describe_str + "', disabled=True, layout=desc_button_layout) \n"
        # print("--- debug: " + desc_row_name + " --> " + describe_str)   #rwh debug

        if (param_count % 2):
            desc_buttons_str += indent + desc_row_name + ".style.button_color = '" + colorname1 + "'\n"
        else:  # rf.  https://www.w3schools.com/colors/colors_names.asp
            desc_buttons_str += indent + desc_row_name + ".style.button_color = '" + colorname2 + "'\n"

    if 'units' in child.attrib.keys():
        if child.attrib['units'] != "dimensionless" and child.attrib['units'] != "none":
#            units_str = child.attrib['units']
            units_count += 1
            units_btn_name = "units_button" + str(units_count)
            units_buttons_str += indent + units_btn_name + " = " + "Button(description='" + child.attrib['units'] + "', disabled=True, layout=units_button_layout) \n"
            if (param_count % 2):
                units_buttons_str += indent + units_btn_name + ".style.button_color = '" + colorname1 + "'\n"
            else:  # rf.  https://www.w3schools.com/colors/colors_names.asp
                units_buttons_str += indent + units_btn_name + ".style.button_color = '" + colorname2 + "'\n"
        else:
            units_count += 1
            units_btn_name = "units_button" + str(units_count)
            units_buttons_str += indent + units_btn_name + " = " + "Button(description='" +  "', disabled=True, layout=units_button_layout) \n"
            if (param_count % 2):
                units_buttons_str += indent + units_btn_name + ".style.button_color = '" + colorname1 + "'\n"
            else:  # rf.  https://www.w3schools.com/colors/colors_names.asp
                units_buttons_str += indent + units_btn_name + ".style.button_color = '" + colorname2 + "'\n"
    else:
        units_count += 1
        units_btn_name = "units_button" + str(units_count)
        units_buttons_str += indent + units_btn_name + " = " + "Button(description='" +  "', disabled=True, layout=units_button_layout) \n"
        if (param_count % 2):
            units_buttons_str += indent + units_btn_name + ".style.button_color = '" + colorname1 + "'\n"
        else:  # rf.  https://www.w3schools.com/colors/colors_names.asp
            units_buttons_str += indent + units_btn_name + ".style.button_color = '" + colorname2 + "'\n"

    if 'type' in child.attrib.keys():
#             self.therapy_activation_time = BoundedFloatText(
#            min=0., max=100000000, step=stepsize,
        full_name = "self." + child.tag
        # name_count += 1
        if child.attrib['type'] not in widgets.keys():
            print("    *** Error - Invalid type: " + child.attrib['type'])
            sys.exit(1)
        else:    
            # The "divider" type elements are unique; let's handle them in their own function
            if divider_flag:
                handle_divider(child)
                continue

            name_count += 1
            param_name_button = "param_name" + str(name_count)
            user_tab_header += "\n" + indent + param_name_button + " = " + "Button(description='" + child.tag + "', disabled=True, layout=name_button_layout)\n"
            if (param_count % 2):
                user_tab_header += indent + param_name_button + ".style.button_color = '" + colorname1 + "'\n"
            else:  # rf.  https://www.w3schools.com/colors/colors_names.asp
                user_tab_header += indent + param_name_button + ".style.button_color = '" + colorname2 + "'\n"
            user_tab_header += "\n" + indent + full_name + " = " + widgets[child.attrib['type']] + "(\n"

            # Try to calculate and provide a "good" delta step (for the tiny "up/down" arrows on a numeric widget)
            if child.attrib['type'] == "double":
                fval_abs = abs(float(child.text))
                if (fval_abs > 0.0):
                    if (fval_abs > 1.0):  # crop
                        delta_val = pow(10, int(math.log10(abs(float(child.text)))) - 1)
                    else:   # round
                        delta_val = pow(10, round(math.log10(abs(float(child.text)))) - 1)
                else:
                    delta_val = 0.01  # if initial value=0.0, we're totally guessing at what a good delta is
                if print_var_types:
                    print('double: ',float(child.text),', delta_val=',delta_val)

                user_tab_header += indent2 + "value=" + child.text + ",\n"
                # Note: "step" values will advance the value to the nearest multiple of the step value itself :-/
                user_tab_header += indent2 + "step=" + str(delta_val) + ",\n"

            # Integers
            elif child.attrib['type'] == "int":  # warning: math.log(1000,10)=2.99..., math.log10(1000)=3  
                if (abs(int(child.text)) > 0):
                    delta_val = pow(10,int(math.log10(abs(int(child.text)))) - 1)
                else:
                    delta_val = 1  # if initial value=0, we're totally guessing at what a good delta is
                if print_var_types:
                    print('int: ',int(child.text),', delta_val=',delta_val)

                user_tab_header += indent2 + "value=" + child.text + ",\n"
                user_tab_header += indent2 + "step=" + str(delta_val) + ",\n"

            # Booleans
            elif child.attrib['type'] == "bool":
                if (child.text.lower() == "true"):
                    child.text = "True"
                elif (child.text.lower() == "false"):
                    child.text = "False"
                else:
                    print(" --- ERROR: bool must be True or False, not ", child.text)
                    sys.exit(1)

                if print_var_types:
                    print('bool: ',child.text)
                user_tab_header += indent2 + "value=" + child.text + ",\n"
            
            # Strings
            elif child.attrib['type'] == "string":
                user_tab_header += indent2 + "value='" + child.text + "',\n"

            # elif child.attrib['type'].lower() == 'divider':
            #     divider_flag = True
            #     child.text = "Worker_Parameters"
            #     # user_tab_header += indent2 + "value=" + child.description + ",\n"
            #     user_tab_header += indent2 + "value=" + child.attrib['description'] + ",\n"


            row_name = "row" + str(param_count)
            box_name = "box" + str(param_count)
            if (not divider_flag):
                # We're processing a "normal" row - typically a name, numeric field, units, description
                #  - append the info at the end of this widget
                user_tab_header += indent2 + "style=style, layout=widget_layout)\n"

                row_str += indent +  row_name + " = [" + param_name_button + ", " + full_name + ", " +      units_btn_name + ", " + desc_row_name + "] \n"

                box_str += indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n"
            else:  # divider
                box_str += indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n"

            vbox_str += indent2 + box_name + ",\n"

            if (not divider_flag):
                # float, int, bool
                if (type_cast[child.attrib['type']] == "bool"):
                    fill_gui_str += indent + full_name + ".value = ('true' == (uep.find('.//" + child.tag + "').text.lower()) )\n"
                else:
                    fill_gui_str += indent + full_name + ".value = " + type_cast[child.attrib['type']] + "(uep.find('.//" + child.tag + "').text)\n"

                fill_xml_str += indent + "uep.find('.//" + child.tag + "').text = str("+ full_name + ".value)\n"

vbox_str += indent + "])"

# Write the beginning of the Python module for the user parameters tab in the GUI
user_tab_file = "user_params.py"
print("\n --------------------------------- ")
print("Generated a new: ", user_tab_file)
print()
fp= open(user_tab_file, 'w')
fp.write(user_tab_header)
fp.write(units_buttons_str)
fp.write(desc_buttons_str)
fp.write(row_str)
fp.write(box_str)
fp.write(vbox_str)
fp.write(fill_gui_str)
fp.write(fill_xml_str)
fp.close()

#---------------------------------------------------------------------------------------------------
#----------  micronenv 
#---------------------------------------------------------------------------------------------------
microenv_tab_header = """ 
# This file is auto-generated from a Python script that parses a PhysiCell configuration (.xml) file.
#
# Edit at your own risk.
#
import os
from ipywidgets import Label,Text,Checkbox,Button,HBox,VBox,FloatText,IntText,BoundedIntText,BoundedFloatText,Layout,Box
    
class MicroenvTab(object):

    def __init__(self):
        
        micron_units = Label('micron')   # use "option m" (Mac, for micro symbol)

        constWidth = '180px'
        tab_height = '500px'
        stepsize = 10

        #style = {'description_width': '250px'}
        style = {'description_width': '25%'}
        layout = {'width': '400px'}

        name_button_layout={'width':'25%'}
        widget_layout = {'width': '15%'}
        widget2_layout = {'width': '10%'}
        units_button_layout ={'width':'15%'}
        desc_button_layout={'width':'45%'}
"""

"""
        self.therapy_activation_time = BoundedFloatText(
            min=0.,
            max=100000000,
            step=stepsize,
            description='therapy_activation_time',
            style=style, layout=layout,
            # layout=Layout(width=constWidth),
        )
        self.save_interval_after_therapy_start = BoundedFloatText(
            min=0.,
            max=100000000,
            step=stepsize,
            description='save_interval_after_therapy_start',
            style=style, layout=layout,
        )

        label_blankline = Label('')

        self.tab = VBox([HBox([self.therapy_activation_time, Label('min')]), 
                         HBox([self.save_interval_after_therapy_start, Label('min')]), 
                         ])  
"""

fill_gui_str= """

    # Populate the GUI widgets with values from the XML
    def fill_gui(self, xml_root):
        uep = xml_root.find('.//microenvironment_setup')  # find unique entry point
        vp = []   # pointers to <variable> nodes
        if uep:
            for var in uep.findall('variable'):
                vp.append(var)

"""

fill_xml_str= """

    # Read values from the GUI widgets to enable editing XML
    def fill_xml(self, xml_root):
        uep = xml_root.find('.//microenvironment_setup')  # find unique entry point
        vp = []   # pointers to <variable> nodes
        if uep:
            for var in uep.findall('variable'):
                vp.append(var)

"""

# Now parse a configuration file (.xml) and map the user parameters into GUI widgets
#tree = ET.parse('../config/PhysiCell_settings.xml')
try:
    tree = ET.parse(config_file)
except:
    print("Cannot parse",config_file, "- check it's XML syntax.")
    sys.exit(1)

root = tree.getroot()

indent = "        "
indent2 = "          "
widgets = {"double":"FloatText", "int":"IntText", "bool":"Checkbox", "string":"Text", "divider":"div"}
type_cast = {"double":"float", "int":"int", "bool":"bool", "string":"", "divider":"div"}
vbox_str = "\n" + indent + "self.tab = VBox([\n"
#param_desc_buttons_str = "\n" 
#name_buttons_str = "\n" 
units_buttons_str = "\n" 
desc_buttons_str = "\n" 
row_str = "\n"
box_str = "\n" + indent + "box_layout = Layout(display='flex', flex_flow='row', align_items='stretch', width='100%')\n"

#        box1 = Box(children=row1, layout=box_layout)\n"

menv_var_count = 0   # micronenv 
param_count = 0
divider_count = 0
color_count = 0
#param_desc_count = 0
name_count = 0
units_count = 0

#----------  micronenv 
	# <microenvironment_setup>
		# <variable name="oxygen" units="mmHg" ID="0">
		# 	<physical_parameter_set>
		# 		<diffusion_coefficient units="micron^2/min">100000.000000</diffusion_coefficient>
		# 		<decay_rate units="1/min">.1</decay_rate>  
		# 	</physical_parameter_set>
		# 	<initial_condition units="mmHg">38.0</initial_condition>
		# 	<Dirichlet_boundary_condition units="mmHg" enabled="true">38.0</Dirichlet_boundary_condition>
		# </variable>
        # ...
        #
        # <options>
		# 	<calculate_gradients>False</calculate_gradients>
		# 	<track_internalized_substrates_in_each_agent>False</track_internalized_substrates_in_each_agent>
			 
		# 	<initial_condition enabled="false" type="matlab">
		# 		<filename>./config/initial.mat</filename>
		# 	</initial_condition>
			 
		# 	<dirichlet_nodes enabled="false" type="matlab">
		# 		<filename>./config/dirichlet.mat</filename>
		# 	</dirichlet_nodes>
		# </options>
	# </microenvironment_setup>
uep = root.find('.//microenvironment_setup')  # find unique entry point (uep) 
if uep:
    fill_gui_str += indent + "uep = xml_root.find('.//microenvironment_setup')  # find unique entry point\n"
    fill_xml_str += indent + "uep = xml_root.find('.//microenvironment_setup')  # find unique entry point\n"
    microenv_tab_header += "\n" 
    pp_count = 0

    units_buttons_str += indent + " #  ------- micronenv info\n"
    var_idx = -1
    # units_buttons_str += indent + " #  --- variable info\n"
    for var in uep.findall('variable'):
        fill_gui_str += "\n"

        var_idx += 1
        menv_var_count += 1
        print('==== new microenv var: ',var.tag, var.attrib)
        # --- basic widgets: 
    #    full_name = "self." + var.attrib['name']
    #    name_count += 1
        # param_name_button = "param_name" + str(name_count)
        #  1) Variable name + [units]
        menv_var_name_button = "menv_var" + str(menv_var_count)
        menv_var_name = var.attrib['name'].replace(" ","_")   # e.g., "director signal" --> "director_signal"
        menv_var_name = menv_var_name.replace("-","_")   # e.g., "pro-inflammatory_cytokine" --> "pro_inflammatory_cytokine"
        print('menv_var_name=',menv_var_name)
        units_str = ''
        if ('units' in var.attrib) and (var.attrib['units'] != 'dimensionless'):
            units_str = ' (' + var.attrib['units'] + ')'
        microenv_tab_header += '\n' + indent + menv_var_name_button + " = " + "Button(description='" + menv_var_name + units_str + "', disabled=True, layout=name_button_layout)\n"
        if (color_count % 2):
            microenv_tab_header += indent + menv_var_name_button + ".style.button_color = '" + colorname1 + "'\n"
        else:  # rf.  https://www.w3schools.com/colors/colors_names.asp
            microenv_tab_header += indent + menv_var_name_button + ".style.button_color = '" + colorname2 + "'\n"
        color_count += 1   # color each menv variable block the same, but alternating color
    #    print(microenv_tab_header)


        # --- row_str: appear AFTER all the basic widgets are defined 
        row_name = "row_" + menv_var_name   # str(param_count)
        # row_str += indent +  row_name + " = [" + param_name_button + ", " + full_name + ", " + units_btn_name + ", " + desc_row_name + "] \n"
        row_str += indent +  row_name + " = [" + menv_var_name_button + ",  ] \n"
        # box_name = "box" + str(param_count)
        box_name = "box_" + menv_var_name
        box_str += indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n"
        vbox_str += indent2 + box_name + ",\n"

        for child in var:  # for every child element of <variable>
#            print(' child in var-----> ',child.tag, child.attrib)
#            print(' child.tag.lower() ----> ',child.tag.lower())

            # if (child.tag.lower == 'physical_parameter_set'):
            if ('physical_parameter_set' in child.tag.lower() ):
            #  2) <physical_parameter_set> variables
                for pp in var.findall('physical_parameter_set'):
                    for ppchild in pp:  # e.g., diffusion_coefficient, decay_rate
#                        print(' -- ppchild in pp: ',ppchild.tag, ppchild.attrib, float(ppchild.text))
                        pp_button_name = "pp_button" + str(pp_count)
                        pp_units_name = "pp_button_units" + str(pp_count)
                        pp_count += 1
                        param_count += 1

                        param_name_button = "menv_param" + str(pp_count)
                        name_count += 1
                        param_name_button = "param_name" + str(name_count)
                        microenv_tab_header += "\n" + indent + param_name_button + " = " + "Button(description='" + ppchild.tag + "', disabled=True, layout=name_button_layout)\n"

                        full_name = "self." + menv_var_name + "_" + ppchild.tag
                        # todo: add stepsize
                        delta_val = get_float_stepsize(ppchild.text)
                        if print_var_types:
                            print('double: ',float(ppchild.text),', delta_val=',delta_val)

                # Note: "step" values will advance the value to the nearest multiple of the step value itself :-/
                # user_tab_header += indent2 + "step=" + str(delta_val) + ",\n"
                        microenv_tab_header += "\n" + indent + full_name + " = FloatText(value=" + ppchild.text + ",\n"
                        microenv_tab_header += indent2 + "step=" + str(delta_val) + ",style=style, layout=widget_layout)\n"

                        fill_gui_str += indent + full_name + ".value = " + 'float' + "(vp["+str(var_idx)+"].find('.//" + ppchild.tag + "').text)\n"

                        fill_xml_str += indent + "vp["+str(var_idx)+"].find('.//" + ppchild.tag + "').text = str("+ full_name + ".value)\n"

                        if 'units' in ppchild.attrib.keys():
                            if ppchild.attrib['units'] != "dimensionless" and ppchild.attrib['units'] != "none":
                                units_btn_name = "menv_units_button" + str(pp_count)
                                units_buttons_str += indent + units_btn_name + " = " + "Button(description='" + ppchild.attrib['units'] + "', disabled=True, layout=units_button_layout) \n"
                            else:
                                units_count += 1
                                units_btn_name = "units_button" + str(units_count)
                                units_buttons_str += indent + units_btn_name + " = " + "Button(description='" +  "', disabled=True, layout=units_button_layout) \n"
                        else:
                            units_count += 1
                            units_btn_name = "units_button" + str(units_count)
                            units_buttons_str += indent + units_btn_name + " = " + "Button(description='" +  "', disabled=True, layout=units_button_layout) \n"

                        row_name = "row" + str(param_count)
                        row_str += indent +  row_name + " = [" + param_name_button + ", " + full_name + ", " + units_btn_name + "]\n"
                        box_name = "box" + str(param_count)
                        box_str += indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n"
                        vbox_str += indent2 + box_name + ",\n"
            #---------------
            elif ('dirichlet_options' in child.tag.lower() ):
                print('------ Found ', child.tag)
                bv_idx = 0
                # bv_widget_names = []
                for bv in child.findall('boundary_value'):
                    bv_idx += 1
                    print('--------- process ', bv.tag, bv.attrib)

                    # Handle the individual boundary Dirichlet BC toggle widgets. So very ugly.
                    if 'enabled' not in bv.attrib.keys():
                        print("******** Error: missing 'enabled' attribute of boundary_value")
                        sys.exit(1)
                    else:
                        toggle_name = full_name + "_toggle_" + bv.attrib['ID']
                        # bv_widget_names.append(toggle_name)
                        print("       toggle_name=",toggle_name)
                        microenv_tab_header += indent + toggle_name + " = Checkbox(description='" + bv.attrib['ID'] + "', disabled=False" + ",style=style, layout=widget_layout)\n"

                        fill_gui_str += indent + "if vp[" + str(var_idx) + "].find('.//boundary_value[" + str(bv_idx) +"]').attrib['enabled'].lower() == 'true':\n"
                        fill_gui_str += indent2 + toggle_name + ".value = True\n"
                        fill_gui_str += indent + "else:\n"
                        fill_gui_str += indent2 + toggle_name + ".value = False\n"

                        menv_var_name = full_name + "_value_" + bv.attrib['ID']

                        # full_name = "self." + menv_var_name + "_" + bv.tag
                        microenv_tab_header += "\n" + indent + menv_var_name + " = FloatText(value=" + bv.text + ",style=style, layout=widget2_layout)\n"

                        # e.g., self.oxygen_Dirichlet_boundary_condition_value_xmin.value = float(vp[0].find('.//Dirichlet_options//boundary_value[1]').text)
                        fill_gui_str += indent + menv_var_name + ".value = " + 'float' + "(vp["+str(var_idx)+"].find('.//" + child.tag + "//boundary_value[" + str(bv_idx) + "]').text)\n"

                        # fill_xml_str += indent + "uep.find('.//" + child.tag + "').text = str("+ full_name + ".value)\n"
                        fill_xml_str += indent + "vp[" + str(var_idx) + "].find('.//" + child.tag + "//boundary_value[" + str(bv_idx) + "]').text = str("+ menv_var_name + ".value)\n"
                    
                    # e.g., vp[0].find('.//Dirichlet_options//boundary_value[1]').attrib['enabled'] = str(self.oxygen_Dirichlet_boundary_condition_toggle_xmin.value).lower()
                        fill_xml_str += indent + "vp[" + str(var_idx) + "].find('.//" + child.tag + "//boundary_value[" + str(bv_idx) + "]').attrib['enabled'] = str(" + toggle_name + ".value).lower()\n\n"


                        param_count += 1
                        row_name = "row" + str(param_count)
                        # row_str += indent +  row_name + " = [" + param_name_button + ", " + full_name + ", " + units_btn_name + "]\n"
                        row_str += indent +  row_name + " = [" + toggle_name + ", " + menv_var_name + ",]\n"
                        box_name = "box" + str(param_count)
                        box_str += indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n"
                        vbox_str += indent2 + box_name + ",\n"


                        # fill_xml_str += indent + "vp[" + str(var_idx) + "].find('.//Dirichlet_boundary_condition').attrib['enabled'] = str(" + toggle_name + ".value).lower()\n\n"

            #---------------
            else:   # in <variable> (not in <physical_parameter_set>), e.g., initial_condition, Dirichlet_boundary_condition
#                print(' >>>> child: ',child.tag, child.attrib, float(child.text))
                pp_button_name = "pp_button" + str(pp_count)
                pp_units_name = "pp_button_units" + str(pp_count)
                pp_count += 1
                param_count += 1

                param_name_button = "menv_param" + str(pp_count)

                name_count += 1
                param_name_button = "param_name" + str(name_count)
                microenv_tab_header += indent + param_name_button + " = " + "Button(description='" + child.tag + "', disabled=True, layout=name_button_layout)\n"

                full_name = "self." + menv_var_name + "_" + child.tag
                microenv_tab_header += "\n" + indent + full_name + " = FloatText(value=" + child.text + ",style=style, layout=widget_layout)\n"

                # fill_gui_str += indent + full_name + ".value = " + 'float' + "(uep.find('.//" + child.tag + "').text)\n"
                fill_gui_str += indent + full_name + ".value = " + 'float' + "(vp["+str(var_idx)+"].find('.//" + child.tag + "').text)\n"

                # fill_xml_str += indent + "uep.find('.//" + child.tag + "').text = str("+ full_name + ".value)\n"
                fill_xml_str += indent + "vp["+str(var_idx)+"].find('.//" + child.tag + "').text = str("+ full_name + ".value)\n"


                # Handle the one-off, Dirichlet BC toggle widget. So very ugly.
                if 'enabled' in child.attrib.keys():
                    # menv_toggle1 = Checkbox(description='on/off', disabled=False, layout=desc_button_layout) 
                    toggle_name = full_name + "_toggle" 
                    microenv_tab_header += indent + toggle_name + " = Checkbox(description='on/off', disabled=False" + ",style=style, layout=widget_layout)\n"

                    # Ugly.
                    # fill_gui_str += indent + full_name + ".value = " + 'float' + "(vp["+str(var_idx)+"].find('.//" + ppchild.tag + "').text)\n"
                    fill_gui_str += indent + "if vp[" + str(var_idx) + "].find('.//Dirichlet_boundary_condition').attrib['enabled'].lower() == 'true':\n"
                    fill_gui_str += indent2 + toggle_name + ".value = True\n"
                    fill_gui_str += indent + "else:\n"
                    fill_gui_str += indent2 + toggle_name + ".value = False\n"

#                    vp[0].find('.//Dirichlet_boundary_condition').attrib['enabled'] = str(self.oxygen_Dirichlet_boundary_condition_toggle.value)
                    fill_xml_str += indent + "vp[" + str(var_idx) + "].find('.//Dirichlet_boundary_condition').attrib['enabled'] = str(" + toggle_name + ".value).lower()\n\n"

                if 'units' in child.attrib.keys():
                    if child.attrib['units'] != "dimensionless" and child.attrib['units'] != "none":
                        units_btn_name = "menv_units_button" + str(pp_count)
                        units_buttons_str += indent + units_btn_name + " = " + "Button(description='" + child.attrib['units'] + "', disabled=True, layout=units_button_layout) \n"
                    else:
                        units_count += 1
                        units_btn_name = "units_button" + str(units_count)
                        units_buttons_str += indent + units_btn_name + " = " + "Button(description='" +  "', disabled=True, layout=units_button_layout) \n"
                else:
                    units_count += 1
                    units_btn_name = "units_button" + str(units_count)
                    units_buttons_str += indent + units_btn_name + " = " + "Button(description='" +  "', disabled=True, layout=units_button_layout) \n"

                row_name = "row" + str(param_count)

                if ("dirichlet_boundary_condition" in child.tag.lower()):
#                    print('----- handle Dirichlet BC checkbox')
                    # dirichlet_toggle_name = "self.toggle_Dirichlet_boundary_condition"
                    # toggle_name = full_name + "_toggle" 
                    row_str += indent +  row_name + " = [" + param_name_button + ", " + full_name + ", " + units_btn_name + ", " + toggle_name + "]\n"
                else:
                    row_str += indent +  row_name + " = [" + param_name_button + ", " + full_name + ", " + units_btn_name + "]\n"

                # if (len(bv_widget_names) > 0):
                #     for bvw in bv_widget_names:
                #         param_count += 1
                #         row_name = "row" + str(param_count)
                #         row_str += indent +  row_name + " = [" + bvw + "]\n"
                #         box_name = "box" + str(param_count)
                #         box_str += indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n"
                #         vbox_str += indent2 + box_name + ",\n"

                # row_str += indent +  row_name + " = [" + param_name_button + ", " + full_name + ", " + units_btn_name + "]\n"
                box_name = "box" + str(param_count)
                box_str += indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n"
                vbox_str += indent2 + box_name + ",\n"


    # units_buttons_str += indent + " #  --- options info\n"
    uep_opt = uep.find('options')
    # gradients_toggle_name = "self." + menv_var_name + "_calculate_gradient"
    # track_toggle_name = "self." + menv_var_name + "_track_internal"
    gradients_toggle_name = "self.calculate_gradient"
    track_toggle_name = "self.track_internal"

    if uep_opt:
#        print('------- found microenv options --------')
        	# <calculate_gradients>true</calculate_gradients>
			# <track_internalized_substrates_in_each_agent>true</track_internalized_substrates_in_each_agent>
        fill_gui_str += "\n"
        fill_xml_str += "\n"
        # print( uep_opt.find('calculate_gradients'))
        elm = uep_opt.find('calculate_gradients') 
        if elm != None:
#            print('---- calculate_gradients')
            microenv_tab_header += indent + gradients_toggle_name + " = Checkbox(description='calculate_gradients', disabled=False, layout=desc_button_layout)\n"
            param_count += 1
            row_name = "row" + str(param_count)
            row_str += indent +  row_name + " = [" + gradients_toggle_name + ",]\n"
            box_name = "box" + str(param_count)
            box_str += indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n"
            vbox_str += indent2 + box_name + ",\n"

            # fill_gui_str += indent + gradients_toggle_name + " = Checkbox(description='calculate_gradients', disabled=False, layout=desc_button_layout)"
            # self.calculate_gradient.value = False
            # if (elm.text.lower() == 'true'):
            #     fill_gui_str += indent + gradients_toggle_name + ".value = True\n"
            # else:
            #     fill_gui_str += indent + gradients_toggle_name + ".value = False\n"

            # fill_gui_str += indent + gradients_toggle_name + ".value = bool(uep.find('.//options//calculate_gradients').text)\n"

            # Ugly.
            fill_gui_str += indent + "if uep.find('.//options//calculate_gradients').text.lower() == 'true':\n"
            fill_gui_str += indent2 + gradients_toggle_name + ".value = True\n"
            fill_gui_str += indent + "else:\n"
            fill_gui_str += indent2 + gradients_toggle_name + ".value = False\n"
#            self.calculate_gradient.value = True
#        else:
#            self.calculate_gradient.value = False

                # rwh
            # self.calculate_gradient.value = bool(uep.find(".//options//calculate_gradients").text)
            # self.track_internal.value = bool(uep.find(".//options//track_internalized_substrates_in_each_agent").text)

            # note that in Python: str(True) --> 'True'
            fill_xml_str += indent + "uep.find('.//options//calculate_gradients').text = str("+ gradients_toggle_name + ".value)\n"

        # uep.find('.//options//calculate_gradients').text = str(self.calculate_gradient.value)
        # uep.find('.//options//track_internalized_substrates_in_each_agent').text = str(self.track_internal.value)

        # if uep_opt.find('foobar') != None:   # testing for false condition
            # print('---- foobar')


        elm = uep_opt.find('track_internalized_substrates_in_each_agent') 
        if elm != None:
#            print('---- track_internalized_substrates_in_each_agent')
            microenv_tab_header += indent + track_toggle_name + " = Checkbox(description='track_in_agents', disabled=False, layout=desc_button_layout)\n"
            param_count += 1
            row_name = "row" + str(param_count)
            row_str += indent +  row_name + " = [" + track_toggle_name + ",]\n"
            box_name = "box" + str(param_count)
            box_str += indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n"
            vbox_str += indent2 + box_name + ",\n"

            # fill_gui_str += indent + "self.calculate_gradients.value = float(uep.find('.//macrophage_relative_adhesion').text)
            # if (elm.text.lower() == 'true'):
            #     fill_gui_str += indent + track_toggle_name + ".value = True\n"
            # else:
            #     fill_gui_str += indent + track_toggle_name + ".value = False\n"

            # fill_gui_str += indent + track_toggle_name + ".value = bool(uep.find('.//options//track_internalized_substrates_in_each_agent').text)\n"

            # Ugly.
            fill_gui_str += indent + "if uep.find('.//options//track_internalized_substrates_in_each_agent').text.lower() == 'true':\n"
            fill_gui_str += indent2 + track_toggle_name + ".value = True\n"
            fill_gui_str += indent + "else:\n"
            fill_gui_str += indent2 + track_toggle_name + ".value = False\n"

            fill_xml_str += indent + "uep.find('.//options//track_internalized_substrates_in_each_agent').text = str("+ track_toggle_name + ".value)\n"


    print('--------- done with microenv --------------')
    fill_gui_str += indent + "\n"
    microenv_tab_header += "\n"
    desc_buttons_str += "\n"
    units_buttons_str += "\n"
    row_str += "\n"

vbox_str += indent + "])"

# Write the beginning of the Python module for the user parameters tab in the GUI
microenv_tab_file = "microenv_params.py"
print("\n --------------------------------- ")
print("Generated a new: ", microenv_tab_file)
print()
#print("If this is your first time:")
#print("Run the GUI via:  jupyter notebook mygui.ipynb")
print("Test the minimal GUI via:  jupyter notebook test_gui.ipynb")
print("run the Jupyter menu item:  Cell -> Run All")
print()
print("(or, if you already have a previous GUI running and want to see new params:")
print("run the Jupyter menu item:  Kernel -> Restart & Run All)")
print()
fp= open(microenv_tab_file, 'w')
fp.write(microenv_tab_header)
fp.write(units_buttons_str)
fp.write(desc_buttons_str)
fp.write(row_str)
fp.write(box_str)
fp.write(vbox_str)
fp.write(fill_gui_str)
fp.write(fill_xml_str)
fp.close()

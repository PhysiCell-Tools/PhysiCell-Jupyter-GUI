"""
====================================================================================================
  Parse a PhysiCell configuration file (XML) and generate a Jupyter (Python) module for 'Cell Types' GUI tab.
  
====================================================================================================
 
  Inputs - takes none, 1, 2, 3, or 4 arguments
  ------
    config filename (str, optional): the PhysiCell configuration file (.xml) (Default = config.xml)
    GUI module (str, optional):      the primary GUI for the Jupyter notebook 
    colorname1, colorname2 (str, optional): the colors to use for the alternating rows of widgets 
                                            (Defaults: lightgreen, tan)
  Examples (with 0,1,2,3,4 args):
  --------
    python create_cell_types.py
    python create_cell_types.py cells.xml
  
  Outputs
  -------
    cell_types.py: Python module used to create/edit cell parameters (--> "Cell Types" GUI tab)
 
Authors:
Randy Heiland (heiland@iu.edu)
Dr. Paul Macklin (macklinp@iu.edu)

--- Versions ---
1.0 - initial version
4.0 - (Oct 2020) for 'Cell Types' tab format, switched from using cell_definition inheritance style to "flat" (verbose) style
4.1 - (Mar 2021) process optional "visible" attribute

"""

import sys
import os
import math
import xml.etree.ElementTree as ET

# Defaults
config_file = "config.xml"
colorname1 = 'lightgreen'
colorname2 = 'tan'
color_idx = 0

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
colorname = [colorname1,colorname2]
print()

if (num_args == 3):
    with open(gui_file) as f:   # e.g., "mygui.py"
    #  newText = f.read().replace('myconfig.xml', config_file) # todo: don't assume this string; find line
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
cells_tab_header = """ 
# This file is auto-generated from a Python script that parses a PhysiCell configuration (.xml) file.
#
# Edit at your own risk.
#
import os
from ipywidgets import Label,Text,Checkbox,Button,HBox,VBox,FloatText,IntText,BoundedIntText,BoundedFloatText,Layout,Box,Dropdown
    
class CellTypesTab(object):

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
        widget_layout_long = {'width': '20%'}
        units_button_layout ={'width':'15%'}
        desc_button_layout={'width':'45%'}
        divider_button_layout={'width':'40%'}
        divider_button_layout={'width':'60%'}
        box_layout = Layout(display='flex', flex_flow='row', align_items='stretch', width='100%')

        self.cell_type_dropdown = Dropdown(description='Cell type:',)
        self.cell_type_dropdown.style = {'description_width': '%sch' % str(len(self.cell_type_dropdown.description) + 1)}

        cell_type_names_layout={'width':'30%'}
        cell_type_names_style={'description_width':'initial'}
        # self.parent_name = Text(value='None',description='inherits properties from parent type:',disabled=True, style=cell_type_names_style, layout=cell_type_names_layout)

        # explain_inheritance = Label(value='    This cell line inherits its properties from its parent type. Any settings below override those inherited properties.')  # , style=cell_type_names_style, layout=cell_type_names_layout)

        # self.cell_type_parent_row = HBox([self.cell_type_dropdown, self.parent_name])
        self.cell_type_parent_row = HBox([self.cell_type_dropdown])
        # self.cell_type_parent_dict = {}
"""


fill_gui_str= """

    # Populate the GUI widgets with values from the XML
    def fill_gui(self, xml_root):
        uep = xml_root.find('.//cell_definitions')  # find unique entry point

"""

fill_xml_str= """

    # Read values from the GUI widgets to enable editing XML
    def fill_xml(self, xml_root):
        uep = xml_root.find('.//cell_definitions')  # find unique entry point

"""

display_cell_type_default = """
    #------------------------------
    def display_cell_type_default(self):
        # print("display_cell_type_default():")
        #print("    self.cell_type_parent_dict = ",self.cell_type_parent_dict)

        # There's probably a better way to do this, but for now,
        # we hide all vboxes containing the widgets for the different cell defs
        # and only display the contents of 'default'
        for vb in self.cell_def_vboxes:
            vb.layout.display = 'none'   # vs. 'contents'
        self.cell_def_vboxes[0].layout.display = 'contents'
"""

cell_type_dropdown_cb = """
    #------------------------------
    def cell_type_cb(self, change):
        if change['type'] == 'change' and change['name'] == 'value':
            # print("changed to %s" % change['new'])
            # self.parent_name.value = self.cell_type_parent_dict[change['new']]
            # idx_selected = list(self.cell_type_parent_dict.keys()).index(change['new'])
            idx_selected = list(self.cell_type_dict.keys()).index(change['new'])

            # print('index=',idx_selected)
            # self.vbox1.layout.visibility = 'hidden'  # vs. visible
            # self.vbox1.layout.visibility = None 

            # There's probably a better way to do this, but for now,
            # we hide all vboxes containing the widgets for the different cell defs
            # and only display the contents of the selected one.
            for vb in self.cell_def_vboxes:
                vb.layout.display = 'none'   # vs. 'contents'
            self.cell_def_vboxes[idx_selected].layout.display = 'contents'   # vs. 'contents'

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
widgets = {"double":"FloatText", "int":"IntText", "bool":"Checkbox", "string":"Text", "divider":""}
#widgets = {"double":"FloatText", "int":"IntText", "bool":"Checkbox", "string":"Text"}
type_cast = {"double":"float", "int":"int", "bool":"bool", "string":"", "divider":"Text"}
main_vbox_str = "\n" + indent + "self.tab = VBox([\n"
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

float_var_count = 0    # FloatText
text_var_count = 0    # Text
bool_var_count = 0     # Checkbox
text_var_count = 0   

button_widget_name = "name_btn"
button_widget_units = "units_btn"

divider_count = 0
color_count = 0
#param_desc_count = 0
name_count = 0
units_count = 0


custom_data_widgets = {"double":"FloatText", "int":"IntText", "bool":"Checkbox", "string":"Text", "divider":""}
custom_data_type_cast = {"double":"float", "int":"int", "bool":"bool", "string":"", "divider":"Text"}

#---------- cell_definitions --------------------
# TODO: cast attributes to lower case before doing equality tests; perform more testing!

uep = root.find('.//cell_definitions')  # find unique entry point (uep) 
# fill_gui_str += indent + "uep = xml_root.find('.//cell_definitions')  # find unique entry point\n"
# fill_xml_str += indent + "uep = xml_root.find('.//cell_definitions')  # find unique entry point\n"

# param_count = 0
   #param_desc_count = 0
# name_count = 0
# units_count = 0

print_vars = False
print_var_types = False

# colors for some dividers
lightorange = '#ffde6b'

tag_list = []

row_name = "row"
def create_row_of_widgets(widget_name_list):
    global row_name, cells_tab_header
  # row_name = "row" 
    # row_str = indent + row_name + " = [" + button_widget_name + ", " + w2 +  ", " + button_widget_units + "]\n"
    row_str = indent + row_name + " = [" 
    for w in widget_name_list:
        row_str +=  w + ", " 

    row_str +=  "]\n" 
    cells_tab_header += row_str

def create_disabled_button_name(name):
    global cells_tab_header, color_idx, button_widget_name
    # # creates "button_widget_name"
    btn_str = indent + button_widget_name + " = Button(description='" + name + "', disabled=True, layout=name_button_layout)\n"
    cells_tab_header += btn_str 
    color_str = indent + button_widget_name + ".style.button_color = '" + colorname[color_idx] + "'\n"
    cells_tab_header += color_str

def create_disabled_button_units(name):
    global cells_tab_header, color_idx, button_widget_units 
    btn_str = indent + button_widget_units + " = Button(description='" + name + "', disabled=True, layout=name_button_layout)\n"
    cells_tab_header += btn_str 
    color_str = indent + button_widget_units + ".style.button_color = '" + colorname[color_idx] + "'\n"
    cells_tab_header += color_str

def get_float_stepsize(val_str):
    fval_abs = abs(float(val_str))
    if (fval_abs > 0.0):
        if (fval_abs > 1.0):  # crop
            delta_val = pow(10, int(math.log10(fval_abs)) - 1)
        else:   # round
            delta_val = pow(10, round(math.log10(fval_abs)) - 1)
    else:
        delta_val = 0.01  # if initial value=0.0, we're totally guessing at what a good delta is
    return delta_val

def create_checkbox_widget(name, desc, val):
    global cells_tab_header, indent
    toggle_str = indent + name + " = Checkbox(description='" + desc + "', value=" + val + ",layout=name_button_layout)\n"
    cells_tab_header += toggle_str
    # return widget_str

def create_float_text_widget(name, initial_val, delta_val):
    global cells_tab_header, indent, indent2
    if delta_val > 0:
        step_val = delta_val
    else:
        step_val = get_float_stepsize(str(initial_val))
    name = name.replace('-','_')
    # cells_tab_header += "------------ create_float_text_widget(), name=  " + name + "\n"
    widget_str = indent + name + " = FloatText(value='" + initial_val + "', step='" + str(step_val) + "', style=style, layout=widget_layout)\n"
    # step=0.1,
    return widget_str

def create_text_widget(name, str_val):
    # substrate_text_str = indent + substrate_name + " = Text(value='" + elm.attrib['name'] + "', disabled=False, style=style, layout=widget_layout)\n"
    widget_str = indent + name + " = Text(value='" + str_val + "', disabled=False, style=style, layout=widget_layout_long)\n"
    return widget_str

# function to process a "divider" type element
def handle_divider(child):
    global divider_count, cells_tab_header, indent, indent2, main_vbox_str
    divider_count += 1
    # print('-----------> handler_divider: ',divider_count)
    divrow_name = "div_row" + str(divider_count)
    cells_tab_header += "\n" + indent + divrow_name + " = " + "Button(description='" + child.attrib['description'] + "', disabled=True, layout=divider_button_layout)\n"
    main_vbox_str += indent2 + divrow_name + ",\n"

def handle_divider_pheno(div_str):
    global divider_count, cells_tab_header, indent, indent2, main_vbox_str
    divider_count += 1
    # print('-----------> handler_divider_pheno: ',divider_count)
    divrow_name = "div_row" + str(divider_count)
    cells_tab_header += indent + "#  ------------------------- \n"
    cells_tab_header += indent + divrow_name + " = " + "Button(description='" + div_str + "', disabled=True, layout=divider_button_layout)\n"
    cells_tab_header += indent + divrow_name + ".style.button_color = 'orange'\n"
    return divrow_name

# default is to assume "float"
def fill_gui_and_xml(widget_name, xml_elm):
    global fill_gui_str, fill_xml_str
    fill_gui_str += indent + widget_name + ".value = float(uep.find('" + xml_elm + "').text)\n"
    fill_xml_str += indent + "uep.find('" + xml_elm + "').text = str(" + widget_name + ".value)\n"

def fill_gui_and_xml_bool_attrib(widget_name, xml_elm, attrib_name):
    global fill_gui_str, fill_xml_str
    # fill_gui_str += indent + widget_name + ".value = ('true' == (uep.find('" + xml_elm + "').text.lower()))\n"
    fill_gui_str += indent + widget_name + ".value = ('true' == (uep.find('" + xml_elm + "').attrib['" + attrib_name + "'].lower()))\n"

    # fill_xml_str += indent + "uep.find('" + xml_elm + "').text = str(" + widget_name + ".value)\n"
    fill_xml_str += indent + "uep.find('" + xml_elm + "').attrib['" + attrib_name + "'] = str(" + widget_name + ".value)\n"

def fill_gui_and_xml_bool(widget_name, xml_elm):
    global fill_gui_str, fill_xml_str
    # self.fix_persistence.value = ('true' == (uep.find('.//fix_persistence').text.lower()) )
    # fill_gui_str += indent + widget_name + ".value = ('true' == (uep.find('" + xml_elm + "').text.lower()))\n"
    fill_gui_str += indent + widget_name + ".value = ('true' == (uep.find('" + xml_elm + "').text.lower()))\n"

    # uep.find('.//fix_persistence').text = str(self.fix_persistence.value)
    # fill_xml_str += indent + "uep.find('" + xml_elm + "').text = str(" + widget_name + ".value)\n"
    fill_xml_str += indent + "uep.find('" + xml_elm + "').text = str(" + widget_name + ".value)\n"

def fill_gui_and_xml_string(widget_name, xml_elm):
    global fill_gui_str, fill_xml_str
    fill_gui_str += indent + widget_name + ".value = uep.find('" + xml_elm + "').text\n"
    fill_xml_str += indent + "uep.find('" + xml_elm + "').text = str(" + widget_name + ".value)\n"

def fill_gui_and_xml_string_attrib(widget_name, xml_elm, attrib_name):
    global fill_gui_str, fill_xml_str
    fill_gui_str += indent + widget_name + ".value = uep.find('" + xml_elm + "').attrib['" + attrib_name + "']\n"
    # fill_xml_str += indent + "uep.find('" + xml_elm + "').text = str(" + widget_name + ".value)\n"
    fill_xml_str += indent + "uep.find('" + xml_elm + "').attrib['" + attrib_name + "'] = str(" + widget_name + ".value)\n"


def fill_gui_and_xml_comment(s):
    global fill_gui_str, fill_xml_str
    fill_gui_str += indent + s + "\n"
    fill_xml_str += indent + s + "\n"

#===========  main loop ===================
ndent = "\n" + indent 
ndent2 = "\n" + indent2

# NOTE: we assume a simple "children-only" hierarchy in <user_parameters>
# for child in uep:   # uep = "unique entry point" for <user_parameters> (from above)

#        self.cell_type.options={'default':'default', 'worker':'worker', 'director':'director', 'cargo':'cargo'}
cells_tab_header += ndent + "self.cell_type_dict = {}"  
#row_name + " = " + "Button(description='" + child.attrib['description'] + "', disabled=True, layout=divider_button_layout)\n"


#--------- Let's do a 3-pass parsing of <cell_definitions> in the .xml file

#--- 1) create a dict ("cell_type_dict") of <cell_definition> names
for child in uep.findall('cell_definition'):
    if print_vars:
        print(child.tag, child.attrib)
        print(child.attrib['name'])
    # cells_tab_header += "'" + child.attrib['name'] + ":'"
    # if child.attrib['name'] != 'default':   # version 4: don't include 'default' in dropdown widget
    if ('visible' in child.attrib.keys() ) and (child.attrib['visible'].lower() == 'false'):   # version 4.1
        pass
    else:
        name_str = "'" + child.attrib['name'] + "'"
        cells_tab_header += ndent + "self.cell_type_dict[" + name_str + "] = " + name_str 

cells_tab_header += ndent + "self.cell_type_dropdown.options = self.cell_type_dict\n"
cells_tab_header += ndent + "self.cell_type_dropdown.observe(self.cell_type_cb)\n"
            
#--- 2) create a dict ("cell_type_parent_dict") of <cell_definition> parents
# for child in uep.findall('cell_definition'):
#     name_str = "'" + child.attrib['name'] + "'"
#     if 'parent_type' in child.attrib:
#         parent_str = "'" + child.attrib['parent_type'] + "'"
#     else:
#         parent_str = "'None'"
#     cells_tab_header += ndent + "self.cell_type_parent_dict[" + name_str + "] = " + parent_str 
# cells_tab_header += "\n\n"
# e.g., self.cell_type_parent_dict =  {'default': 'None', 'lung epithelium': 'default', 'immune': 'default', 'CD8 Tcell': 'immune', 'macrophage': 'immune', 'neutrophil': 'immune'}


# main_vbox_str += indent2 + "self.cell_type_parent_row, explain_inheritance, \n"
main_vbox_str += indent2 + "self.cell_type_parent_row,  \n"
#    cells_tab_header += "\n" + indent + row_name + " = " + "Button(description='" + child.attrib['description'] + "', disabled=True, layout=divider_button_layout)\n"


cells_tab_header += ndent + "self.cell_def_vboxes = []\n" 

motility_count = 0
cell_def_count = 0
box_count = 0

#--- 3) primary pass to generate all ipywidgets Python code, initialize their values from those 
#       in the .xml, and generate code for the 2 functions, "fill_gui" and "fill_xml"
#       
for cell_def in uep.findall('cell_definition'):
    color_idx = 0
    cell_def_name = cell_def.attrib['name']
    uep_phenotype = cell_def.find('phenotype')  # cell_def children: currently just <phenotype> and <custom_data> 

    cells_tab_header += indent + "#  >>>>>>>>>>>>>>>>> <cell_definition> = " + cell_def.attrib['name'] + "\n"

    subpath0 = ".//cell_definition[" + str(cell_def_count+1) + "]" + "//phenotype"

    print("\n---------------- subpath0 ",cell_def.attrib['name'], " = ", subpath0)
    fill_gui_and_xml_comment("# ------------------ cell_definition: " + cell_def.attrib['name'])

    #   print('pheno=',uep_phenotype)
    prefix = 'phenotype:'

    elm_str = ""   # element string: this will contain all widget names that go into this cell def VBox

    rate_count = 0
    for child in uep_phenotype:
        print('pheno child=',child)
        if child.tag == 'cycle':  # <cycle code="6" name="flow_cytometry_separated_cycle_model">
            cycle_name = ""
            if 'name' in child.attrib.keys():   
                cycle_name = child.attrib['name']

            cycle_code = ""
            if 'code' in child.attrib.keys():   
                cycle_code = child.attrib['code']

            fill_gui_and_xml_comment("# ---------  cycle (" + cycle_name + ")")  

            subpath1 = subpath0  + "//" + child.tag

            # print('cycle code=',child.attrib['code'])
            # print('cycle name=',child.attrib['name'])

            divider_pheno_name = handle_divider_pheno(prefix + child.tag + " (model: " + cycle_name + "; code=" + cycle_code + ")" ) 
            elm_str += divider_pheno_name + ", "
            # print(elm_str)
            color_str = indent + divider_pheno_name + ".style.button_color = '" + colorname[color_idx] + "'\n"

            # <phase_durations units="min"> 
            #     <duration index="0" fixed_duration="false">300.0</duration>
            for cycle_child in child:
                if cycle_child.tag == 'phase_durations':
                    subpath2 = subpath1 +  "//phase_durations"
                    units_str = ""
                    if 'units' in cycle_child.attrib.keys():
                        units_str = cycle_child.attrib['units']
                    duration_count = 0
                    for duration_elm in cycle_child:
                        w0 = "self.bool" + str(bool_var_count)
                        bool_var_count += 1

                        duration_count += 1
                        subpath3 = subpath2 +  "//duration[" + str(duration_count) + "]"

                        if duration_elm.attrib['fixed_duration'].lower() == 'true':
                            val = "True"
                        else:
                            val = "False"
                        attrib_name = 'fixed_duration'
                        toggle_str = indent + w0 + " = Checkbox(description='" + attrib_name + "', value=" + val + ",layout=name_button_layout)\n"
                        cells_tab_header += toggle_str
                        # create_checkbox_widget(w0, attrib_name, val)

                        fill_gui_and_xml_bool_attrib(w0, subpath3, attrib_name)

                        btn_name = "duration"
                        create_disabled_button_name(btn_name)  # creates "button_widget_name"

                        w2 = "self.float" + str(float_var_count)
                        float_var_count += 1
                        cells_tab_header += create_float_text_widget(w2, duration_elm.text, -1)

                        fill_gui_and_xml(w2,subpath3)

                        create_disabled_button_units(units_str)  # creates "button_widget_units"
                        color_idx = 1 - color_idx

                        create_row_of_widgets([w0, button_widget_name, w2, button_widget_units])

                        box_name = "box" + str(box_count) 
                        box_count += 1
                        box_str = indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n\n"
                        cells_tab_header += box_str 
                        elm_str += box_name + ", "


                elif cycle_child.tag == 'phase_transition_rates':
                    subpath2 = subpath1 + "//" + cycle_child.tag
                    # print("\n---------------- subpath2 = ", subpath2)
                    for rates in child:
                        units_str = ""
                        if 'units' in rates.attrib.keys():
                            units_str = rates.attrib['units']
                        rate_count = 0
                        for rate in rates:
                            # btn_name = "transition rate: " + rate.attrib['start_index'] + "->" + rate.attrib['end_index']
                            btn_name = "Phase " + rate.attrib['start_index'] + " -> Phase " + rate.attrib['end_index'] + " transition rate"
                            create_disabled_button_name(btn_name)  # creates "button_widget_name"

                            w2 = "self.float" + str(float_var_count)
                            float_var_count += 1
                            cells_tab_header += create_float_text_widget(w2, rate.text, -1)

                            rate_count += 1

                            subpath = subpath2 +  "//rate[" + str(rate_count) + "]"

                            fill_gui_and_xml(w2, subpath)

                            create_disabled_button_units(units_str)  # creates "button_widget_units"
                            color_idx = 1 - color_idx

                            # row_name = "row" 
                            # row_str = indent + row_name + " = [" + button_widget_name + ", " + w2 +  ", " + button_widget_units + "]\n"
                            # cells_tab_header += row_str
                            create_row_of_widgets([button_widget_name, w2, button_widget_units])

                            box_name = "box" + str(box_count) 
                            box_count += 1
                            box_str = indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n\n"
                            cells_tab_header += box_str 
                            elm_str += box_name + ", "


        elif child.tag == 'death':
            fill_gui_and_xml_comment("# ---------  death ") 

            subpath1 = subpath0  + "//" + child.tag
            death_model_count = 0
            elm_str += handle_divider_pheno(prefix + child.tag) + ", "
            for death_model in child:
                death_model_count += 1
                subpath2 = subpath1 +  "//model[" + str(death_model_count) + "]"

                death_row_name = "death_model" + str(death_model_count)
                death_header_str = indent + death_row_name + " = " + "Button(description='model: " + death_model.attrib['name'] + "', disabled=True, layout={'width':'30%'})\n"
                cells_tab_header += death_header_str 
                cells_tab_header += indent + death_row_name + ".style.button_color = '" + lightorange + "'\n" 
                elm_str += death_row_name + ","

                # print('death code=',death_model.attrib['code'])
                # print('death name=',death_model.attrib['name'])

                #----------  overall death model rate -------------
                rate = death_model.find('.//death_rate')  
                subpath3 = subpath2 +  "//death_rate"

                create_disabled_button_name("death rate")  # creates "button_widget_name"

                w2 = "self.float" + str(float_var_count)
                float_var_count += 1
                cells_tab_header += create_float_text_widget(w2, rate.text, -1)

                create_disabled_button_units(units_str)  # creates "button_widget_units"
                color_idx = 1 - color_idx

                fill_gui_and_xml(w2, subpath3)

                # row_name = "row"
                # row_str = indent + row_name + " = [" + button_widget_name + ", " + w2 +  ", " + button_widget_units + "]\n"
                # cells_tab_header += row_str
                create_row_of_widgets([button_widget_name, w2, button_widget_units])

                box_name = "box" + str(box_count) 
                box_count += 1
                box_str = indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n\n"
                cells_tab_header += box_str 
                elm_str += box_name + ", "

                #----------  death model transition rate(s) -------------
                t_rate = death_model.find('.//transition_rates')  
                if t_rate:
                    rate_count = 1
                    subpath3 = subpath2 +  "//transition_rates" 
                    # print('t_rate units=',t_rate.attrib['units'])
                    for rate in t_rate:
                        w0 = "self.bool" + str(bool_var_count)
                        bool_var_count += 1

                        subpath4 = subpath3 +  "//rate[" + str(rate_count) + "]"
                        rate_count += 1
                        # print("\n---------------- subpath4 = ", subpath4)

                        if rate.attrib['fixed_duration'].lower() == 'true':
                            val = "True"
                        else:
                            val = "False"
                        attrib_name = 'fixed_duration'
                        toggle_str = indent + w0 + " = Checkbox(description='" + attrib_name + "', value=" + val + ",layout=name_button_layout)\n"
                        cells_tab_header += toggle_str

                        fill_gui_and_xml_bool_attrib(w0, subpath4, attrib_name)

                        # btn_name = "transition rate: " + rate.attrib['start_index'] + "->" + rate.attrib['end_index']

                        # <transition_rates units="1/min">
							# <rate start_index="0" end_index="1" fixed_duration="true">0.00193798</rate>
						# </transition_rates>
                        if death_model.attrib['name'].lower() == 'apoptosis':
                          btn_name = "exit rate from apoptotic phase"
                        elif death_model.attrib['name'].lower() == 'necrosis': 
                            if rate.attrib['start_index'] == "0":
                                btn_name = "exit rate from necrotic swelling phase"
                            elif rate.attrib['start_index'] == "1":
                                btn_name = "exit rate from necrotic lysed phase"
                        else:
                            print("\n >>>>>>>WARNING: invalid death model name: ",death_model.attrib['name'])
                        # elif death_model.attrib['name'].lower() == 'autophagy':


                        create_disabled_button_name(btn_name)  # creates "button_widget_name"

                        w2 = "self.float" + str(float_var_count)
                        float_var_count += 1
                        cells_tab_header += create_float_text_widget(w2, rate.text, -1)

                        fill_gui_and_xml(w2,subpath4)

                        create_disabled_button_units(units_str)  # creates "button_widget_units"
                        color_idx = 1 - color_idx

                        # row_name = "row"
                        # row_str = indent + row_name + " = [" + w0 + ", " + button_widget_name + ", " + w2 +  ", " + button_widget_units + "]\n"
                        # cells_tab_header += row_str
                        create_row_of_widgets([w0, button_widget_name, w2, button_widget_units])

                        box_name = "box" + str(box_count) 
                        box_count += 1
                        box_str = indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n\n"
                        cells_tab_header += box_str 
                        elm_str += box_name + ", "

                #----------  death model <parameters> -------------
                d_params = death_model.find('.//parameters')  
                if d_params:
                    subpath3 = subpath2 +  "//parameters" 
                    for elm in d_params:
                        subpath4 = subpath3 +  "//" + elm.tag 
                        create_disabled_button_name(elm.tag)  # creates "button_widget_name"

                        w2 = "self.float" + str(float_var_count)
                        float_var_count += 1
                        cells_tab_header += create_float_text_widget(w2, elm.text, -1)

                        fill_gui_and_xml(w2,subpath4)

                        create_disabled_button_units(units_str)  # creates "button_widget_units"
                        color_idx = 1 - color_idx

                        # row_name = "row" 
                        # row_str = indent + row_name + " = [" + button_widget_name + ", " + w2 +  ", " + button_widget_units + "]\n"
                        # cells_tab_header += row_str
                        create_row_of_widgets([button_widget_name, w2, button_widget_units])

                        box_name = "box" + str(box_count) 
                        box_count += 1
                        box_str = indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n\n"
                        cells_tab_header += box_str 
                        elm_str += box_name + ", "

        elif child.tag == 'volume':
            fill_gui_and_xml_comment("# ---------  volume ") 

            elm_str += handle_divider_pheno(prefix + "volume") + ", "

            subpath1 = subpath0  + "//" + child.tag
            # print("\n---------------- subpath1 = ", subpath1)
            for elm in child:
                subpath2 = subpath1 +  "//" + elm.tag 
                create_disabled_button_name(elm.tag)  # creates "button_widget_name"

                w2 = "self.float" + str(float_var_count)
                float_var_count += 1
                cells_tab_header += create_float_text_widget(w2, elm.text, -1)

                fill_gui_and_xml(w2, subpath2)

                create_disabled_button_units(units_str)  # creates "button_widget_units"
                color_idx = 1 - color_idx

                # row_name = "row" 
                # row_str = indent + row_name + " = [" + button_widget_name + ", " + w2 +  ", " + button_widget_units + "]\n"
                # cells_tab_header += row_str
                create_row_of_widgets([button_widget_name, w2, button_widget_units])

                box_name = "box" + str(box_count) 
                box_count += 1
                box_str = indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n\n"
                cells_tab_header += box_str 
                elm_str += box_name + ", "

        elif child.tag == 'mechanics':
            fill_gui_and_xml_comment("# ---------  mechanics ") 

            elm_str += handle_divider_pheno(prefix + "mechanics") + ", "
            subpath1 = subpath0  + "//" + child.tag

            for elm in child:
                if elm.tag == 'options':
                    subpath2 = subpath1  + "//" + elm.tag
                    for opt_elm in elm:
                        subpath3 = subpath2  + "//" + opt_elm.tag
                        w0 = "self.bool" + str(bool_var_count)
                        bool_var_count += 1
                        if opt_elm.attrib['enabled'].lower() == 'true':
                            val = "True"
                        else:
                            val = "False"
                        toggle_str = indent + w0 + " = Checkbox(description='enabled', value=" + val + ",layout=name_button_layout)\n"
                        cells_tab_header += toggle_str

                        fill_gui_and_xml_bool_attrib(w0, subpath3, 'enabled')

                        create_disabled_button_name(opt_elm.tag)  # creates "button_widget_name"

                        w2 = "self.float" + str(float_var_count)
                        float_var_count += 1
                        cells_tab_header += create_float_text_widget(w2, opt_elm.text, -1)

                        create_disabled_button_units(units_str)  # creates "button_widget_units"
                        color_idx = 1 - color_idx

                        # row_name = "row" 
                        # row_str = indent + row_name + " = [" + w0 + ", " + button_widget_name + ", " + w2 +  ", " + button_widget_units + "]\n"
                        # cells_tab_header += row_str
                        create_row_of_widgets([w0, button_widget_name, w2, button_widget_units])

                        box_name = "box" + str(box_count) 
                        box_count += 1
                        box_str = indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n\n"
                        cells_tab_header += box_str 
                        elm_str += box_name + ", "
                else:
                    subpath2 = subpath1 +  "//" + elm.tag 
                    create_disabled_button_name(elm.tag)  # creates "button_widget_name"

                    w2 = "self.float" + str(float_var_count)
                    float_var_count += 1
                    cells_tab_header += create_float_text_widget(w2, elm.text, -1)

                    fill_gui_and_xml(w2, subpath2)

                    create_disabled_button_units(units_str)  # creates "button_widget_units"
                    color_idx = 1 - color_idx

                    # row_name = "row" 
                    # row_str = indent + row_name + " = [" + button_widget_name + ", " + w2 +  ", " + button_widget_units + "]\n"
                    # cells_tab_header += row_str
                    create_row_of_widgets([button_widget_name, w2, button_widget_units])

                if elm.tag != 'options':
                    box_name = "box" + str(box_count) 
                    box_count += 1
                    box_str = indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n\n"
                    cells_tab_header += box_str 
                    elm_str += box_name + ", "


        elif child.tag == 'motility':
            fill_gui_and_xml_comment("# ---------  motility ") 

            motility_count += 1
            elm_str += handle_divider_pheno(prefix + "motility") + ", "
            subpath1 = subpath0  + "//" + child.tag

            for elm in child:
                if elm.tag == 'options':
                    subpath2 = subpath1  + "//" + elm.tag
                    for opt_elm in elm:
                        if opt_elm.tag == 'enabled':
                            subpath3 = subpath2  + "//" + opt_elm.tag
                            w0 = "self.bool" + str(bool_var_count)
                            bool_var_count += 1
                            if opt_elm.text.lower() == 'true':
                                val = "True"
                            else:
                                val = "False"
                            toggle_str = indent + w0 + " = Checkbox(description='enabled', value=" + val + ",layout=name_button_layout)\n"
                            cells_tab_header += toggle_str
                            elm_str += w0 + ","

                            fill_gui_and_xml_bool(w0, subpath3)

                        elif opt_elm.tag == 'use_2D':
                            subpath3 = subpath2  + "//" + opt_elm.tag
                            w0 = "self.bool" + str(bool_var_count)
                            bool_var_count += 1
                            if opt_elm.text.lower() == 'true':
                                val = "True"
                            else:
                                val = "False"
                            toggle_str = indent + w0 + " = Checkbox(description='use_2D', value=" + val + ",layout=name_button_layout)\n"
                            cells_tab_header += toggle_str
                            elm_str += w0 + ","

                            fill_gui_and_xml_bool(w0, subpath3)

                        elif opt_elm.tag == 'chemotaxis':
                            subpath3 = subpath2  + "//" + opt_elm.tag
                            cells_tab_header += "\n"
                            chemo_row_name = "chemotaxis_btn"
                            chemo_header_str = indent + chemo_row_name + " = " + "Button(description='chemotaxis', disabled=True, layout={'width':'30%'})\n"
                            cells_tab_header += chemo_header_str 
                            cells_tab_header += indent + chemo_row_name + ".style.button_color = '" + lightorange + "'\n" 
                            elm_str += chemo_row_name + ","

                            for chemotaxis_elm in opt_elm:
                                cells_tab_header += "\n"
                                if chemotaxis_elm.tag == 'enabled':
                                    subpath4 = subpath3  + "//" + chemotaxis_elm.tag
                                    w0 = "self.bool" + str(bool_var_count)
                                    bool_var_count += 1
                                    if opt_elm.text.lower() == 'true':
                                        val = "True"
                                    else:
                                        val = "False"
                                    toggle_str = indent + w0 + " = Checkbox(description='enabled', value=" + val + ",layout=name_button_layout)\n"
                                    cells_tab_header += toggle_str
                                    elm_str += w0 + ","

                                    fill_gui_and_xml_bool(w0, subpath4)

                                elif chemotaxis_elm.tag == 'substrate':
                                    subpath4 = subpath3  + "//" + chemotaxis_elm.tag

                                    create_disabled_button_name(chemotaxis_elm.tag)  # creates "button_widget_name"
                                    color_idx = 1 - color_idx

                                    substrate_name = "self.chemotaxis_substrate" + str(motility_count)

                                    cells_tab_header += create_text_widget(substrate_name, chemotaxis_elm.text)

                                    fill_gui_and_xml_string(substrate_name, subpath4)

                                    row_str = indent + "row = [" + button_widget_name + ", " + substrate_name + "]\n"
                                    cells_tab_header += row_str

                                    box_name = "box" + str(box_count)
                                    box_count += 1
                                    box_str = indent + box_name + " = Box(children=row, layout=box_layout)\n"
                                    cells_tab_header += box_str
                                    elm_str += box_name + ","

                                elif chemotaxis_elm.tag == 'direction':
                                    subpath4 = subpath3  + "//" + chemotaxis_elm.tag

                                    create_disabled_button_name("direction")  # creates "button_widget_name"

                                    direction_name = "self.chemotaxis_direction" + str(motility_count)

                                    cells_tab_header += create_text_widget(direction_name, chemotaxis_elm.text)
                                    
                                    fill_gui_and_xml_string(direction_name, subpath4)

                                    row_str = indent + "row = [" + button_widget_name + ", " + direction_name + "]\n"
                                    cells_tab_header += row_str
                                    color_idx = 1 - color_idx
                                    box_name = "box" + str(box_count)
                                    box_count += 1
                                    box_str = indent + box_name + " = Box(children=row, layout=box_layout)\n"
                                    cells_tab_header += box_str
                                    elm_str += box_name + ","
                    continue

                subpath2 = subpath1 +  "//" + elm.tag 

                cells_tab_header += "\n"
                create_disabled_button_name(elm.tag)  # creates "button_widget_name"

                w2 = "self.float" + str(float_var_count)
                float_var_count += 1
                cells_tab_header += create_float_text_widget(w2, elm.text, -1)

                fill_gui_and_xml(w2, subpath2)

                units_str = ""
                if 'units' in elm.attrib.keys():
                    units_str = elm.attrib['units']
                    # units_str = elm.attrib['units']
                    # name_units = child.tag + '_' + elm.tag + "units" + str(motility_count)
                    # btn_str = indent + name_units + " = Button(description='" + units_str + "', disabled=True, layout=units_button_layout)\n"
                    # cells_tab_header += btn_str

                    # color_str = indent + name_units + ".style.button_color = '" + colorname[color_idx] + "'\n"
                    # cells_tab_header += color_str
                create_disabled_button_units(units_str)  # creates "button_widget_units"

                color_idx = 1 - color_idx

                # motility_row3 = [name_btn, self.motility_migration_bias1 , units_btn]
                row_str = indent + "row = [" + button_widget_name + ", " + w2 + ", " +  button_widget_units + "]\n"
                cells_tab_header += row_str
                # motility_box3 = Box(children=motility_row3, layout=box_layout)
                box_name = "box" + str(box_count)
                box_count += 1
                box_str = indent + box_name + " = Box(children=row, layout=box_layout)\n"
                cells_tab_header += box_str
                elm_str += box_name + ","


        elif child.tag == 'secretion':
            fill_gui_and_xml_comment("# ---------  secretion ") 

            elm_str += handle_divider_pheno(prefix + "secretion") + ", "
            subpath1 = subpath0  + "//" + child.tag
            substrate_count = 0
            for elm in child:
                if elm.tag == 'substrate':
                    substrate_count += 1
                    subpath2 = subpath1  + "//" + elm.tag + "[" + str(substrate_count) + "]"
                    print(subpath2)

                    create_disabled_button_name("substrate")  # creates "button_widget_name"

                    substrate_name = "self.text" + str(text_var_count)
                    text_var_count += 1
                    cells_tab_header += create_text_widget(substrate_name, elm.attrib['name'])

                    fill_gui_and_xml_string_attrib(substrate_name, subpath2, 'name')

                    row_str = indent + "row = [" + button_widget_name + ", " + substrate_name + "]\n"
                    cells_tab_header += row_str
                    color_idx = 1 - color_idx

                    box_name = "box" + str(box_count)
                    box_count += 1
                    box_str = indent + box_name + " = Box(children=row, layout=box_layout)\n"
                    cells_tab_header += box_str
                    elm_str += box_name + ","
                    # substrate_count += 1

                    for sub_elm in elm:
                        subpath3 = subpath2  + "//" + sub_elm.tag
                        create_disabled_button_name(sub_elm.tag)  # creates "button_widget_name"

                        w2 = "self.float" + str(float_var_count)
                        float_var_count += 1
                        cells_tab_header += create_float_text_widget(w2, sub_elm.text, -1)

                        fill_gui_and_xml(w2, subpath3)

                        if 'units' in sub_elm.attrib.keys():
                            # units_str = sub_elm.attrib['units']
                            # name_units = 'name_units'
                            # btn_str = indent + name_units + " = Button(description='" + units_str + "', disabled=True, layout=units_button_layout)\n"
                            # cells_tab_header += btn_str

                            # color_str = indent + name_units + ".style.button_color = '" + colorname[color_idx] + "'\n"
                            # cells_tab_header += color_str
                            create_disabled_button_units(sub_elm.attrib['units'])  # creates "button_widget_units"

                        color_idx = 1 - color_idx

                        row_str = indent + "row = [" + button_widget_name + ", " + w2 + ", " +  button_widget_units + "]\n"
                        cells_tab_header += row_str
                        box_name = "box" + str(box_count)
                        box_count += 1
                        box_str = indent + box_name + " = Box(children=row, layout=box_layout)\n"
                        cells_tab_header += box_str
                        elm_str += box_name + ","


        elif child.tag == 'molecular':
            fill_gui_and_xml_comment("# ---------  molecular") 

            elm_str += handle_divider_pheno(prefix + "molecular") + ", "
            subpath1 = subpath0  + "//" + child.tag


    #------------  process <custom_data>  ----------------------------------------
    # TODO: CLEAN UP THIS MESS
    # thought I might attempt to re-use the xml2jupyter code for <user_parameters>, but ...

    # custom_data_widgets = {"double":"FloatText", "int":"IntText", "bool":"Checkbox", "string":"Text", "divider":""}
    # custom_data_type_cast = {"double":"float", "int":"int", "bool":"bool", "string":"", "divider":"Text"}

    uep_custom_data = cell_def.find('custom_data')

    cells_tab_header += "\n#      ================== <custom_data>, if present ==================\n"
    param_count = float_var_count + 1

    if uep_custom_data:  # if there are no elements in <custom_data>, we don't show the empty divider 
        print("\n  >>>  parse <custom_data> for " + cell_def.attrib['name'] )
        divider_count += 1
        row_name = "div_row" + str(divider_count)
        cells_tab_header += "\n" + indent + row_name + " = " + "Button(description='Custom Data',disabled=True, layout=divider_button_layout)\n"
        cells_tab_header += indent + row_name + ".style.button_color = 'cyan'\n"
        elm_str += row_name + ","

        #---- create widgets:  name, value (float, bool?, string?), units, description
        # for now, we assume only float values

        for cd in uep_custom_data:   
            if print_vars:
                print(' >> custom_data:  ',cd.tag, cd.attrib)

            create_disabled_button_name(cd.tag)   # creates "button_widget_name"

            w2 = "self.float" + str(float_var_count)
            float_var_count += 1
            cells_tab_header += create_float_text_widget(w2, cd.text, -1)

            # w3 = "units_btn" 
            units_str = ""
            if 'units' in cd.attrib.keys():
                units_str = cd.attrib['units']
            # else:
            # btn_str = indent + w3 + " = Button(description='" + units_str + "', disabled=True, layout=units_button_layout)\n"
            # cells_tab_header += btn_str

            # color_str = indent + w3 + ".style.button_color = '" + colorname[color_idx] + "'\n"
            # cells_tab_header += color_str
            create_disabled_button_units(units_str)  # creates "button_widget_units"

            w4 = "description_btn" 
            if 'description' in cd.attrib.keys():
                description_str = cd.attrib['description']
            else:
                description_str = ""
            btn_str = indent + w4 + " = Button(description='" + description_str + "', disabled=True, layout=desc_button_layout)\n"
            cells_tab_header += btn_str

            color_str = indent + w4 + ".style.button_color = '" + colorname[color_idx] + "'\n"
            cells_tab_header += color_str

            color_idx = 1 - color_idx

            row_name = "row"
            row_str = indent +  row_name + " = [" + button_widget_name + ", " + w2 + ", " +  button_widget_units + ", " + w4 + "] \n"

            cells_tab_header += row_str + "\n"

            box_name = "box" + str(box_count)
            box_count += 1
            cells_tab_header += indent + box_name + " = Box(children=" + row_name + ", layout=box_layout)\n"

            elm_str += indent2 + box_name + ",\n"


    #======================================================================
    #------------  assemble VBox for this cell type
    #   if uep_custom_data:  # if there are no elements in <custom_data>, we don't show the empty divider 
    cell_def_count_end = cell_def_count
    vbox_name = "self.cell_def_vbox%d" % cell_def_count
    cell_def_vbox_str = "\n" + indent + vbox_name + " = VBox([\n"
    cell_def_vbox_str += indent2 + elm_str
    cell_def_vbox_str += indent + "])\n"

    if cell_def_count >= 0:  # NOTE: kind of assuming 0th is "default"
        main_vbox_str += vbox_name + ", " 

    cells_tab_header += cell_def_vbox_str
    cells_tab_header += indent + "# ------------------------------------------\n"

    cells_tab_header += indent + "self.cell_def_vboxes.append(" + vbox_name + ")\n\n"
    cell_def_count += 1


main_vbox_str += indent + "])"


# Write the beginning of the Python module for the 'Cell Types' tab in the GUI
# cells_tab_file = "cells_def.py"
cells_tab_file = "cell_types.py"
print("\n --------------------------------- ")
print("Generated a new: ", cells_tab_file)
print()
fp= open(cells_tab_file, 'w')
fp.write(cells_tab_header)
fp.write(units_buttons_str)
fp.write(desc_buttons_str)
fp.write(row_str)
fp.write(box_str)
fp.write(main_vbox_str)
fp.write(cell_type_dropdown_cb)
fp.write(display_cell_type_default)
fp.write(fill_gui_str)
fp.write(fill_xml_str)
fp.close()


#=================================================================
print()
#print("If this is your first time:")
#print("Run the GUI via:  jupyter notebook mygui.ipynb")
print("Test the minimal GUI via:  jupyter notebook test_gui.ipynb")
print("run the Jupyter menu item:  Cell -> Run All")
print()
print("(or, if you already have a previous GUI running and want to see new params:")
print("run the Jupyter menu item:  Kernel -> Restart & Run All)")
print()
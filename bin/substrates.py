# substrates  Tab

import os, math
from pathlib import Path
from ipywidgets import Layout, Label, Text, Checkbox, Button, BoundedIntText, HBox, VBox, Box, \
    FloatText, Dropdown, interactive
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle, Ellipse, Rectangle
from matplotlib.collections import PatchCollection
import matplotlib.colors as mplc
from collections import deque
import numpy as np
import scipy.io
import xml.etree.ElementTree as ET  # https://docs.python.org/2/library/xml.etree.elementtree.html
import glob
import platform
import zipfile
from debug import debug_view 
import warnings

hublib_flag = True
if platform.system() != 'Windows':
    try:
#        print("Trying to import hublib.ui")
        from hublib.ui import Download
    except:
        hublib_flag = False
else:
    hublib_flag = False

#warnings.warn(message, mplDeprecation, stacklevel=1)
warnings.filterwarnings("ignore")

class SubstrateTab(object):

    def __init__(self):
        
        self.output_dir = '.'
        # self.output_dir = 'tmpdir'

        self.figsize_width_substrate = 15.0  # allow extra for colormap
        self.figsize_height_substrate = 12.5
        self.figsize_width_svg = 12.0
        self.figsize_height_svg = 12.0

        # self.fig = plt.figure(figsize=(7.2,6))  # this strange figsize results in a ~square contour plot

        self.first_time = True
        self.modulo = 1

        self.use_defaults = True

        self.svg_delta_t = 1
        self.substrate_delta_t = 1
        self.svg_frame = 1
        self.substrate_frame = 1

        self.customized_output_freq = False
        self.therapy_activation_time = 1000000
        self.max_svg_frame_pre_therapy = 1000000
        self.max_substrate_frame_pre_therapy = 1000000

        self.svg_xmin = 0

        # Probably don't want to hardwire these if we allow changing the domain size
        # self.svg_xrange = 2000
        # self.xmin = -1000.
        # self.xmax = 1000.
        # self.ymin = -1000.
        # self.ymax = 1000.
        # self.x_range = 2000.
        # self.y_range = 2000.

        self.show_nucleus = False
        self.show_edge = True

        # Paul's additions in Nov 2020
        self.bgcolor = [1,1,1]
        self.dark_mode = True; 
        self.enable_alpha = True; 
        self.default_alpha = 0.4

        # initial value
        self.field_index = 4
        # self.field_index = self.mcds_field.value + 4

        self.skip_cb = False

        # define dummy size of mesh (set in the tool's primary module)
        self.numx = 0
        self.numy = 0

        self.title_str = ''

        tab_height = '600px'
        tab_height = '500px'
        constWidth = '180px'
        constWidth2 = '150px'
        tab_layout = Layout(width='900px',   # border='2px solid black',
                            height=tab_height, ) #overflow_y='scroll')

        max_frames = 1   
        # self.mcds_plot = interactive(self.plot_substrate, frame=(0, max_frames), continuous_update=False)  
        # self.i_plot = interactive(self.plot_plots, frame=(0, max_frames), continuous_update=False)  
        self.i_plot = interactive(self.plot_substrate, frame=(0, max_frames), continuous_update=False)  

        # "plot_size" controls the size of the tab height, not the plot (rf. figsize for that)
        # NOTE: the Substrates Plot tab has an extra row of widgets at the top of it (cf. Cell Plots tab)
        svg_plot_size = '700px'
        svg_plot_size = '600px'
        svg_plot_size = '700px'
        svg_plot_size = '900px'
        self.i_plot.layout.width = svg_plot_size
        self.i_plot.layout.height = svg_plot_size

        self.fontsize = 20

            # description='# cell frames',
        self.max_frames = BoundedIntText(
            min=0, max=99999, value=max_frames,
            description='# frames',
           layout=Layout(width='160px'),
        )
        self.max_frames.observe(self.update_max_frames)

        # self.field_min_max = {'dummy': [0., 1., False]}
        # NOTE: manually setting these for now (vs. parsing them out of data/initial.xml)
        self.field_min_max = {'director signal':[0.,1.,False], 'cargo signal':[0.,1.,False] }
        # hacky I know, but make a dict that's got (key,value) reversed from the dict in the Dropdown below
        # self.field_dict = {0:'dummy'}
        self.field_dict = {0:'director signal', 1:'cargo signal'}

        self.mcds_field = Dropdown(
            options={'director signal': 0, 'cargo signal':1},
            value=0,
            #     description='Field',
           layout=Layout(width=constWidth)
        )
        # print("substrate __init__: self.mcds_field.value=",self.mcds_field.value)
#        self.mcds_field.observe(self.mcds_field_cb)
        self.mcds_field.observe(self.mcds_field_changed_cb)

        self.field_cmap = Dropdown(
            options=['viridis', 'jet', 'YlOrRd'],
            value='YlOrRd',
            #     description='Field',
           layout=Layout(width=constWidth)
        )
#        self.field_cmap.observe(self.plot_substrate)
        self.field_cmap.observe(self.mcds_field_cb)

        self.cmap_fixed_toggle = Checkbox(
            description='Fixed substrate range',
            disabled=False,
            value=False,
#           layout=Layout(width=constWidth2),
        )
        self.cmap_fixed_toggle.observe(self.mcds_field_cb)

#         def cmap_fixed_toggle_cb(b):
#             # self.update()
# #            self.field_min_max = {'oxygen': [0., 30.,True], 'glucose': [0., 1.,False]}
#             field_name = self.field_dict[self.mcds_field.value]
#             if (self.cmap_fixed_toggle.value):  
#                 self.field_min_max[field_name][0] = self.cmap_min.value
#                 self.field_min_max[field_name][1] = self.cmap_max.value
#                 self.field_min_max[field_name][2] = True
#             else:
#                 # self.field_min_max[field_name][0] = self.cmap_min.value
#                 # self.field_min_max[field_name][1] = self.cmap_max.value
#                 self.field_min_max[field_name][2] = False
#             self.i_plot.update()

        # self.cmap_fixed_toggle.observe(cmap_fixed_toggle_cb)

#         self.save_min_max= Button(
#             description='Save', #style={'description_width': 'initial'},
#             button_style='success',  # 'success', 'info', 'warning', 'danger' or ''
#             tooltip='Save min/max for this substrate',
#             disabled=True,
#            layout=Layout(width='90px')
#         )

#         def save_min_max_cb(b):
# #            field_name = self.mcds_field.options[]
# #            field_name = next(key for key, value in self.mcds_field.options.items() if value == self.mcds_field.value)
#             field_name = self.field_dict[self.mcds_field.value]
# #            print(field_name)
# #            self.field_min_max = {'oxygen': [0., 30.], 'glucose': [0., 1.], 'H+ ions': [0., 1.], 'ECM': [0., 1.], 'NP1': [0., 1.], 'NP2': [0., 1.]}
#             self.field_min_max[field_name][0] = self.cmap_min.value
#             self.field_min_max[field_name][1] = self.cmap_max.value
# #            print(self.field_min_max)

#         self.save_min_max.on_click(save_min_max_cb)


        self.cmap_min = FloatText(
            description='Min',
            value=0,
            step = 0.1,
            disabled=True,
            layout=Layout(width=constWidth2),
        )
        self.cmap_min.observe(self.mcds_field_cb)

        self.cmap_max = FloatText(
            description='Max',
            value=38,
            step = 0.1,
            disabled=True,
            layout=Layout(width=constWidth2),
        )
        self.cmap_max.observe(self.mcds_field_cb)

        def cmap_fixed_toggle_cb(b):
            field_name = self.field_dict[self.mcds_field.value]
            # print(self.cmap_fixed_toggle.value)
            if (self.cmap_fixed_toggle.value):  # toggle on fixed range
                self.cmap_min.disabled = False
                self.cmap_max.disabled = False
                self.field_min_max[field_name][0] = self.cmap_min.value
                self.field_min_max[field_name][1] = self.cmap_max.value
                self.field_min_max[field_name][2] = True
                # self.save_min_max.disabled = False
            else:  # toggle off fixed range
                self.cmap_min.disabled = True
                self.cmap_max.disabled = True
                self.field_min_max[field_name][2] = False
                # self.save_min_max.disabled = True
#            self.mcds_field_cb()
            self.i_plot.update()

        self.cmap_fixed_toggle.observe(cmap_fixed_toggle_cb)

        field_cmap_row2 = HBox([self.field_cmap, self.cmap_fixed_toggle])

#        field_cmap_row3 = HBox([self.save_min_max, self.cmap_min, self.cmap_max])
        items_auto = [
            # self.save_min_max, #layout=Layout(flex='3 1 auto', width='auto'),
            self.cmap_min, 
            self.cmap_max,  
         ]
        box_layout = Layout(display='flex',
                    flex_flow='row',
                    align_items='stretch',
                    width='80%')
        field_cmap_row3 = Box(children=items_auto, layout=box_layout)

        # self.debug_str = Text(
        #     value='debug info',
        #     description='Debug:',
        #     disabled=True,
        #     layout=Layout(width='600px'),  #constWidth = '180px'
        # )

        #---------------------
        self.cell_nucleus_toggle = Checkbox(
            description='nuclei',
            disabled=False,
            value = self.show_nucleus,
#           layout=Layout(width=constWidth2),
        )
        def cell_nucleus_toggle_cb(b):
            # self.update()
            if (self.cell_nucleus_toggle.value):  
                self.show_nucleus = True
            else:
                self.show_nucleus = False
            self.i_plot.update()

        self.cell_nucleus_toggle.observe(cell_nucleus_toggle_cb)

        #----
        self.cell_edges_toggle = Checkbox(
            description='edges',
            disabled=False,
            value=self.show_edge,
#           layout=Layout(width=constWidth2),
        )
        def cell_edges_toggle_cb(b):
            # self.update()
            if (self.cell_edges_toggle.value):  
                self.show_edge = True
            else:
                self.show_edge = False
            self.i_plot.update()

        self.cell_edges_toggle.observe(cell_edges_toggle_cb)

        self.cell_alpha_toggle = Checkbox(
            description='transparency',
            disabled=False,
            value=self.enable_alpha, 
        )
        def cell_alpha_toggle_cb(b):
            #print( 'yay ')
            if( self.cell_alpha_toggle.value):
                self.enable_alpha = True
                #print( 'enable') 
            else:
                self.enable_alpha = False 
                #print( 'disable')
            self.i_plot.update()

        self.cell_alpha_toggle.observe(cell_alpha_toggle_cb)

        self.cells_toggle = Checkbox(
            description='Cells',
            disabled=False,
            value=True,
#           layout=Layout(width=constWidth2),
        )
        def cells_toggle_cb(b):
            # self.update()
            self.i_plot.update()
            if (self.cells_toggle.value):
                self.cell_edges_toggle.disabled = False
                self.cell_nucleus_toggle.disabled = False
            else:
                self.cell_edges_toggle.disabled = True
                self.cell_nucleus_toggle.disabled = True

        self.cells_toggle.observe(cells_toggle_cb)


        self.dark_mode_toggle = Checkbox(
            description='dark mode',
            disabled=False,
            value=self.dark_mode, 
        )
        def dark_mode_toggle_cb(b):
            #print( 'yay ')
            if( self.dark_mode_toggle.value):
                self.dark_mode = True
                self.bgcolor = [0,0,0,1]
                #print( 'enable') 
            else:
                self.dark_mode = False 
                self.bgcolor = [1,1,1,1]
                #print( 'disable')
            self.i_plot.update()

        self.dark_mode_toggle.observe(dark_mode_toggle_cb)



        #---------------------
        self.substrates_toggle = Checkbox(
            description='Substrates',
            disabled=False,
            value=True,
#           layout=Layout(width=constWidth2),
        )
        def substrates_toggle_cb(b):
            if (self.substrates_toggle.value):  # seems bass-ackwards
                self.cmap_fixed_toggle.disabled = False
                self.cmap_min.disabled = False
                self.cmap_max.disabled = False
                self.mcds_field.disabled = False
                self.field_cmap.disabled = False
            else:
                self.cmap_fixed_toggle.disabled = True
                self.cmap_min.disabled = True
                self.cmap_max.disabled = True
                self.mcds_field.disabled = True
                self.field_cmap.disabled = True

        self.substrates_toggle.observe(substrates_toggle_cb)

        self.grid_toggle = Checkbox(
            description='grid',
            disabled=False,
            value=True,
#           layout=Layout(width=constWidth2),
        )
        def grid_toggle_cb(b):
            # self.update()
            self.i_plot.update()

        self.grid_toggle.observe(grid_toggle_cb)

#        field_cmap_row3 = Box([self.save_min_max, self.cmap_min, self.cmap_max])

        # mcds_tab = widgets.VBox([mcds_dir, mcds_plot, mcds_play], layout=tab_layout)
        # mcds_params = VBox([self.mcds_field, field_cmap_row2, field_cmap_row3, self.max_frames])  # mcds_dir
#        mcds_params = VBox([self.mcds_field, field_cmap_row2, field_cmap_row3,])  # mcds_dir

#        self.tab = HBox([mcds_params, self.mcds_plot], layout=tab_layout)

        help_label = Label('select slider: drag or left/right arrows')
        # row1 = Box([help_label, Box( [self.max_frames, self.mcds_field, self.field_cmap], layout=Layout(border='0px solid black',
        row1a = Box( [self.max_frames, self.mcds_field, self.field_cmap], layout=Layout(border='1px solid black',
                            width='50%',
                            height='',
                            align_items='stretch',
                            flex_direction='row',
                            display='flex')) 
        # row1b = Box( [self.cells_toggle, self.cell_nucleus_toggle, self.cell_edges_toggle, self.cell_alpha_toggle], layout=Layout(border='1px solid black',
        row1b = Box( [self.cells_toggle, self.cell_edges_toggle, self.cell_alpha_toggle], layout=Layout(border='1px solid black',
                            width='50%',
                            height='',
                            align_items='stretch',
                            flex_direction='row',
                            display='flex')) 
        row1 = HBox( [row1a, Label('.....'), row1b])

        row2a = Box([self.cmap_fixed_toggle, self.cmap_min, self.cmap_max], layout=Layout(border='1px solid black',
                            width='50%',
                            height='',
                            align_items='stretch',
                            flex_direction='row',
                            display='flex'))
        # row2b = Box( [self.substrates_toggle, self.grid_toggle], layout=Layout(border='1px solid black',
        row2b = Box( [self.substrates_toggle, self.dark_mode_toggle ], layout=Layout(border='1px solid black',
                            width='50%',
                            height='',
                            align_items='stretch',
                            flex_direction='row',
                            display='flex')) 
        # row2 = HBox( [row2a, self.substrates_toggle, self.grid_toggle])
        row2 = HBox( [row2a, Label('.....'), row2b])

        if (hublib_flag):
            self.download_button = Download('mcds.zip', style='warning', icon='cloud-download', 
                                                tooltip='Download data', cb=self.download_cb)

            self.download_svg_button = Download('svg.zip', style='warning', icon='cloud-download', 
                                            tooltip='You need to allow pop-ups in your browser', cb=self.download_svg_cb)

            self.download_settings_button = Download('config.zip', style='warning', icon='cloud-download',
                                            tooltip='Download XML configuration (settings) file.', cb=self.download_settings_cb )

            download_row = HBox([self.download_button.w, self.download_svg_button.w, self.download_settings_button.w, Label("Download all cell plots (browser must allow pop-ups).")])

            # box_layout = Layout(border='0px solid')
            controls_box = VBox([row1, row2])  # ,width='50%', layout=box_layout)
            self.tab = VBox([controls_box, self.i_plot, download_row])
            # self.tab = VBox([controls_box, self.debug_str, self.i_plot, download_row])
        else:
            # self.tab = VBox([row1, row2])
            self.tab = VBox([row1, row2, self.i_plot])

    #---------------------------------------------------
    def update_dropdown_fields(self, data_dir):
        # print('update_dropdown_fields called --------')
        self.output_dir = data_dir
        tree = None
        try:
            fname = os.path.join(self.output_dir, "initial.xml")
            tree = ET.parse(fname)
            xml_root = tree.getroot()
        except:
            print("Cannot open ",fname," to read info, e.g., names of substrate fields.")
            return

        xml_root = tree.getroot()
        self.field_min_max = {}
        self.field_dict = {}
        dropdown_options = {}
        uep = xml_root.find('.//variables')
        comment_str = ""
        field_idx = 0
        if (uep):
            for elm in uep.findall('variable'):
                # print("-----> ",elm.attrib['name'])
                field_name = elm.attrib['name']
                self.field_min_max[field_name] = [0., 1., False]
                self.field_dict[field_idx] = field_name
                dropdown_options[field_name] = field_idx

                self.field_min_max[field_name][0] = 0   
                self.field_min_max[field_name][1] = 1

                # self.field_min_max[field_name][0] = field_idx   #rwh: helps debug
                # self.field_min_max[field_name][1] = field_idx+1   
                self.field_min_max[field_name][2] = False
                field_idx += 1

#        constWidth = '180px'
        # print('options=',dropdown_options)
        # print(self.field_min_max)  # debug
        self.mcds_field.value = 0
        self.mcds_field.options = dropdown_options
#         self.mcds_field = Dropdown(
# #            options={'oxygen': 0, 'glucose': 1},
#             options=dropdown_options,
#             value=0,
#             #     description='Field',
#            layout=Layout(width=constWidth)
#         )

    # def update_max_frames_expected(self, value):  # called when beginning an interactive Run
    #     self.max_frames.value = value  # assumes naming scheme: "snapshot%08d.svg"
    #     self.mcds_plot.children[0].max = self.max_frames.value

#------------------------------------------------------------------------------
    def update_params(self, config_tab, user_params_tab):
        # xml_root.find(".//x_min").text = str(self.xmin.value)
        # xml_root.find(".//x_max").text = str(self.xmax.value)
        # xml_root.find(".//dx").text = str(self.xdelta.value)
        # xml_root.find(".//y_min").text = str(self.ymin.value)
        # xml_root.find(".//y_max").text = str(self.ymax.value)
        # xml_root.find(".//dy").text = str(self.ydelta.value)
        # xml_root.find(".//z_min").text = str(self.zmin.value)
        # xml_root.find(".//z_max").text = str(self.zmax.value)
        # xml_root.find(".//dz").text = str(self.zdelta.value)

        self.xmin = config_tab.xmin.value 
        self.xmax = config_tab.xmax.value 
        self.x_range = self.xmax - self.xmin
        self.svg_xrange = self.xmax - self.xmin
        self.ymin = config_tab.ymin.value
        self.ymax = config_tab.ymax.value 
        self.y_range = self.ymax - self.ymin

        self.numx =  math.ceil( (self.xmax - self.xmin) / config_tab.xdelta.value)
        self.numy =  math.ceil( (self.ymax - self.ymin) / config_tab.ydelta.value)

        if (self.x_range > self.y_range):  
            ratio = self.y_range / self.x_range
            self.figsize_width_substrate = 15.0  # allow extra for colormap
            self.figsize_height_substrate = 12.5 * ratio
            self.figsize_width_svg = 12.0
            self.figsize_height_svg = 12.0 * ratio
        else:   # x < y
            ratio = self.x_range / self.y_range
            self.figsize_width_substrate = 15.0 * ratio 
            self.figsize_height_substrate = 12.5
            self.figsize_width_svg = 12.0 * ratio
            self.figsize_height_svg = 12.0 

        self.svg_flag = config_tab.toggle_svg.value
        self.substrates_flag = config_tab.toggle_mcds.value
        # print("substrates: update_params(): svg_flag, toggle=",self.svg_flag,config_tab.toggle_svg.value)        
        # print("substrates: update_params(): self.substrates_flag = ",self.substrates_flag)
        self.svg_delta_t = config_tab.svg_interval.value
        self.substrate_delta_t = config_tab.mcds_interval.value
        self.modulo = int(self.substrate_delta_t / self.svg_delta_t)
        # print("substrates: update_params(): modulo=",self.modulo)        

        if self.customized_output_freq:
#            self.therapy_activation_time = user_params_tab.therapy_activation_time.value   # NOTE: edit for user param name
            # print("substrates: update_params(): therapy_activation_time=",self.therapy_activation_time)
            self.max_svg_frame_pre_therapy = int(self.therapy_activation_time/self.svg_delta_t)
            self.max_substrate_frame_pre_therapy = int(self.therapy_activation_time/self.substrate_delta_t)

#------------------------------------------------------------------------------
#    def update(self, rdir):
#   Called from driver module (e.g., pc4*.py) (among other places?)
    def update(self, rdir=''):
        # with debug_view:
        #     print("substrates: update rdir=", rdir)        
        # print("substrates: update rdir=", rdir)        

        if rdir:
            self.output_dir = rdir

        # print('update(): self.output_dir = ', self.output_dir)

        if self.first_time:
        # if True:
            self.first_time = False
            full_xml_filename = Path(os.path.join(self.output_dir, 'config.xml'))
            # print("substrates: update(), config.xml = ",full_xml_filename)        
            # self.num_svgs = len(glob.glob(os.path.join(self.output_dir, 'snap*.svg')))
            # self.num_substrates = len(glob.glob(os.path.join(self.output_dir, 'output*.xml')))
            # print("substrates: num_svgs,num_substrates =",self.num_svgs,self.num_substrates)        
            # argh - no! If no files created, then denom = -1
            # self.modulo = int((self.num_svgs - 1) / (self.num_substrates - 1))
            # print("substrates: update(): modulo=",self.modulo)        
            if full_xml_filename.is_file():
                tree = ET.parse(str(full_xml_filename))  # this file cannot be overwritten; part of tool distro
                xml_root = tree.getroot()
                self.svg_delta_t = float(xml_root.find(".//SVG//interval").text)
                self.substrate_delta_t = float(xml_root.find(".//full_data//interval").text)
                # print("substrates: svg,substrate delta_t values=",self.svg_delta_t,self.substrate_delta_t)        
                self.modulo = int(self.substrate_delta_t / self.svg_delta_t)
                # print("substrates: update(): modulo=",self.modulo)        


        # all_files = sorted(glob.glob(os.path.join(self.output_dir, 'output*.xml')))  # if the substrates/MCDS

        all_files = sorted(glob.glob(os.path.join(self.output_dir, 'snap*.svg')))   # if .svg
        if len(all_files) > 0:
            last_file = all_files[-1]
            self.max_frames.value = int(last_file[-12:-4])  # assumes naming scheme: "snapshot%08d.svg"
        else:
            substrate_files = sorted(glob.glob(os.path.join(self.output_dir, 'output*.xml')))
            if len(substrate_files) > 0:
                last_file = substrate_files[-1]
                self.max_frames.value = int(last_file[-12:-4])

    def download_svg_cb(self):
        file_str = os.path.join(self.output_dir, '*.svg')
        # print('zip up all ',file_str)
        with zipfile.ZipFile('svg.zip', 'w') as myzip:
            for f in glob.glob(file_str):
                myzip.write(f, os.path.basename(f))   # 2nd arg avoids full filename path in the archive

    def download_settings_cb(self):
        file_str = os.path.join(self.output_dir, 'config.zip')
        with zipfile.ZipFile('config.zip','w') as myzip:
            for f in glob.glob(file_str):
                myzip.write(f, os.path.basename(f))   # 2nd arg avoids full filename path in the archive

    def download_cb(self):
        file_xml = os.path.join(self.output_dir, '*.xml')
        file_mat = os.path.join(self.output_dir, '*.mat')
        # print('zip up all ',file_str)
        with zipfile.ZipFile('mcds.zip', 'w') as myzip:
            for f in glob.glob(file_xml):
                myzip.write(f, os.path.basename(f)) # 2nd arg avoids full filename path in the archive
            for f in glob.glob(file_mat):
                myzip.write(f, os.path.basename(f))

    def update_max_frames(self,_b):
        self.i_plot.children[0].max = self.max_frames.value

    # called if user selected different substrate in dropdown
    def mcds_field_changed_cb(self, b):
        # print("mcds_field_changed_cb: self.mcds_field.value=",self.mcds_field.value)
        if (self.mcds_field.value == None):
            return
        self.field_index = self.mcds_field.value + 4

        field_name = self.field_dict[self.mcds_field.value]
        # print('mcds_field_changed_cb: field_name='+ field_name)
        # print(self.field_min_max[field_name])
        # self.debug_str.value = 'mcds_field_changed_cb: '+ field_name  + str(self.field_min_max[field_name])
        # self.debug_str.value = 'cb1: '+ str(self.field_min_max)

        # BEWARE of these triggering the mcds_field_cb() callback! Hence, the "skip_cb"
        self.skip_cb = True
        self.cmap_min.value = self.field_min_max[field_name][0]
        self.cmap_max.value = self.field_min_max[field_name][1]
        self.cmap_fixed_toggle.value = bool(self.field_min_max[field_name][2])
        self.skip_cb = False

        self.i_plot.update()

    # called if user provided different min/max values for colormap, or a different colormap
    def mcds_field_cb(self, b):
        if self.skip_cb:
            return

        self.field_index = self.mcds_field.value + 4

        field_name = self.field_dict[self.mcds_field.value]
        # print('mcds_field_cb: field_name='+ field_name)

        # print('mcds_field_cb: '+ field_name)
        self.field_min_max[field_name][0] = self.cmap_min.value 
        self.field_min_max[field_name][1] = self.cmap_max.value
        self.field_min_max[field_name][2] = self.cmap_fixed_toggle.value
        # print(self.field_min_max[field_name])
        # self.debug_str.value = 'mcds_field_cb: ' + field_name + str(self.field_min_max[field_name])
        # self.debug_str.value = 'cb2: '+ str(self.field_min_max)
        # print('--- cb2: '+ str(self.field_min_max))  #rwh2
        # self.cmap_fixed_toggle.value = self.field_min_max[field_name][2]

        # field_name = self.mcds_field.options[self.mcds_field.value]
        # self.cmap_min.value = self.field_min_max[field_name][0]  # oxygen, etc
        # self.cmap_max.value = self.field_min_max[field_name][1]  # oxygen, etc

#        self.field_index = self.mcds_field.value + 4
#        print('field_index=',self.field_index)
        self.i_plot.update()


    #---------------------------------------------------------------------------
    def circles(self, x, y, s, c='b', vmin=None, vmax=None, **kwargs):
        """
        See https://gist.github.com/syrte/592a062c562cd2a98a83 

        Make a scatter plot of circles. 
        Similar to plt.scatter, but the size of circles are in data scale.
        Parameters
        ----------
        x, y : scalar or array_like, shape (n, )
            Input data
        s : scalar or array_like, shape (n, ) 
            Radius of circles.
        c : color or sequence of color, optional, default : 'b'
            `c` can be a single color format string, or a sequence of color
            specifications of length `N`, or a sequence of `N` numbers to be
            mapped to colors using the `cmap` and `norm` specified via kwargs.
            Note that `c` should not be a single numeric RGB or RGBA sequence 
            because that is indistinguishable from an array of values
            to be colormapped. (If you insist, use `color` instead.)  
            `c` can be a 2-D array in which the rows are RGB or RGBA, however. 
        vmin, vmax : scalar, optional, default: None
            `vmin` and `vmax` are used in conjunction with `norm` to normalize
            luminance data.  If either are `None`, the min and max of the
            color array is used.
        kwargs : `~matplotlib.collections.Collection` properties
            Eg. alpha, edgecolor(ec), facecolor(fc), linewidth(lw), linestyle(ls), 
            norm, cmap, transform, etc.
        Returns
        -------
        paths : `~matplotlib.collections.PathCollection`
        Examples
        --------
        a = np.arange(11)
        circles(a, a, s=a*0.2, c=a, alpha=0.5, ec='none')
        plt.colorbar()
        License
        --------
        This code is under [The BSD 3-Clause License]
        (http://opensource.org/licenses/BSD-3-Clause)
        """

        if np.isscalar(c):
            kwargs.setdefault('color', c)
            c = None

        if 'fc' in kwargs:
            kwargs.setdefault('facecolor', kwargs.pop('fc'))
        if 'ec' in kwargs:
            kwargs.setdefault('edgecolor', kwargs.pop('ec'))
        if 'ls' in kwargs:
            kwargs.setdefault('linestyle', kwargs.pop('ls'))
        if 'lw' in kwargs:
            kwargs.setdefault('linewidth', kwargs.pop('lw'))
        # You can set `facecolor` with an array for each patch,
        # while you can only set `facecolors` with a value for all.

        zipped = np.broadcast(x, y, s)
        patches = [Circle((x_, y_), s_)
                for x_, y_, s_ in zipped]
        collection = PatchCollection(patches, **kwargs)
        if c is not None:
            c = np.broadcast_to(c, zipped.shape).ravel()
            collection.set_array(c)
            collection.set_clim(vmin, vmax)

        ax = plt.gca()
        ax.add_collection(collection)
        ax.autoscale_view()
        # plt.draw_if_interactive()
        if c is not None:
            plt.sci(collection)
        # return collection

    #------------------------------------------------------------
    # def plot_svg(self, frame, rdel=''):
    def plot_svg(self, frame):
        # global current_idx, axes_max
        global current_frame
        current_frame = frame
        fname = "snapshot%08d.svg" % frame
        full_fname = os.path.join(self.output_dir, fname)
        # with debug_view:
            # print("plot_svg:", full_fname) 
        # print("-- plot_svg:", full_fname) 
        if not os.path.isfile(full_fname):
            print("Once output files are generated, click the slider.")   
            return

        # set background color 
        bgcolor = self.bgcolor;  # 1.0 for white 

        xlist = deque()
        ylist = deque()
        rlist = deque()
        rgba_list = deque() # Paul Nov 2020 

        #  print('\n---- ' + fname + ':')
#        tree = ET.parse(fname)
        tree = ET.parse(full_fname)
        root = tree.getroot()
        #  print('--- root.tag ---')
        #  print(root.tag)
        #  print('--- root.attrib ---')
        #  print(root.attrib)
        #  print('--- child.tag, child.attrib ---')
        numChildren = 0
        for child in root:
            #    print(child.tag, child.attrib)
            #    print("keys=",child.attrib.keys())
            if self.use_defaults and ('width' in child.attrib.keys()):
                self.axes_max = float(child.attrib['width'])
                # print("debug> found width --> axes_max =", axes_max)
            if child.text and "Current time" in child.text:
                svals = child.text.split()
                # remove the ".00" on minutes
                self.title_str += "   cells: " + svals[2] + "d, " + svals[4] + "h, " + svals[7][:-3] + "m"

                # self.cell_time_mins = int(svals[2])*1440 + int(svals[4])*60 + int(svals[7][:-3])
                # self.title_str += "   cells: " + str(self.cell_time_mins) + "m"   # rwh

            # print("width ",child.attrib['width'])
            # print('attrib=',child.attrib)
            # if (child.attrib['id'] == 'tissue'):
            if ('id' in child.attrib.keys()):
                # print('-------- found tissue!!')
                tissue_parent = child
                break

        # print('------ search tissue')
        cells_parent = None

        for child in tissue_parent:
            # print('attrib=',child.attrib)
            if (child.attrib['id'] == 'cells'):
                # print('-------- found cells, setting cells_parent')
                cells_parent = child
                break
            numChildren += 1

        num_cells = 0
        #  print('------ search cells')
        for child in cells_parent:
            #    print(child.tag, child.attrib)
            #    print('attrib=',child.attrib)
            for circle in child:  # two circles in each child: outer + nucleus
                #  circle.attrib={'cx': '1085.59','cy': '1225.24','fill': 'rgb(159,159,96)','r': '6.67717','stroke': 'rgb(159,159,96)','stroke-width': '0.5'}
                #      print('  --- cx,cy=',circle.attrib['cx'],circle.attrib['cy'])
                xval = float(circle.attrib['cx'])

                # map SVG coords into comp domain
                # xval = (xval-self.svg_xmin)/self.svg_xrange * self.x_range + self.xmin
                xval = xval/self.x_range * self.x_range + self.xmin

                s = circle.attrib['fill']
                # print("s=",s)
                # print("type(s)=",type(s))
                if( s[0:4] == "rgba" ):
                    background = bgcolor[0] * 255.0; # coudl also be 255.0 for white
                    rgba_float =list(map(float,s[5:-1].split(",")))
                    r = rgba_float[0]
                    g = rgba_float[1]
                    b = rgba_float[2]
                    alpha = rgba_float[3]
                    alpha *= 2.0; # cell_alpha_toggle
                    if( not self.enable_alpha or (alpha > 1.0) ):
                        alpha = 1.0
                    rgba = [1,1,1,alpha]
                    rgba[0:3] = [ np.round(r), np.round(g), np.round(b) ];  
                    rgba[0:3] = [x / 255. for x in rgba[0:3] ]  
                elif (s[0:3] == "rgb" ):  # if an rgb string, e.g. "rgb(175,175,80)" 
                    rgba = [1,1,1,1.0]
                    if( self.enable_alpha ):
                        rgba = [1,1,1,self.default_alpha]
                    rgba[0:3] = list(map(int, s[4:-1].split(",")))  
                    rgba[0:3] = [x / 255. for x in rgba[0:3] ]
                else:     # otherwise, must be a color name
                    rgb_tuple = mplc.to_rgb(mplc.cnames[s])  # a tuple
                    rgba = [1,1,1,1.0]
                    rgba[0:3] = [x for x in rgb_tuple]
                # test for bogus x,y locations (rwh TODO: use max of domain?)
                too_large_val = 10000.
                if (np.fabs(xval) > too_large_val):
                    print("bogus xval=", xval)
                    break
                yval = float(circle.attrib['cy'])
                # yval = (yval - self.svg_xmin)/self.svg_xrange * self.y_range + self.ymin
                yval = yval/self.y_range * self.y_range + self.ymin
                if (np.fabs(yval) > too_large_val):
                    print("bogus xval=", xval)
                    break

                rval = float(circle.attrib['r'])
                # if (rgb[0] > rgb[1]):
                #     print(num_cells,rgb, rval)
                xlist.append(xval)
                ylist.append(yval)
                rlist.append(rval)

                rgba_list.append(rgba)

                # For .svg files with cells that *have* a nucleus, there will be a 2nd
                if (not self.show_nucleus):
                    break

            num_cells += 1

            # if num_cells > 3:   # for debugging
            #   print(fname,':  num_cells= ',num_cells," --- debug exit.")
            #   sys.exit(1)
            #   break

            # print(fname,':  num_cells= ',num_cells)

        xvals = np.array(xlist)
        yvals = np.array(ylist)
        rvals = np.array(rlist)

        rgbas = np.array(rgba_list)
        # print("xvals[0:5]=",xvals[0:5])
        # print("rvals[0:5]=",rvals[0:5])
        # print("rvals.min, max=",rvals.min(),rvals.max())

        # rwh - is this where I change size of render window?? (YES - yipeee!)
        #   plt.figure(figsize=(6, 6))
        #   plt.cla()
        # if (self.substrates_toggle.value):
        self.title_str += " (" + str(num_cells) + " agents)"
            # title_str = " (" + str(num_cells) + " agents)"
        # else:
            # mins= round(int(float(root.find(".//current_time").text)))  # TODO: check units = mins
            # hrs = int(mins/60)
            # days = int(hrs/24)
            # title_str = '%dd, %dh, %dm' % (int(days),(hrs%24), mins - (hrs*60))
        plt.title(self.title_str)

        plt.xlim(self.xmin, self.xmax)
        plt.ylim(self.ymin, self.ymax)

        ax = plt.gca()
        ax.set_facecolor(bgcolor)

        #   plt.xlim(axes_min,axes_max)
        #   plt.ylim(axes_min,axes_max)
        #   plt.scatter(xvals,yvals, s=rvals*scale_radius, c=rgbs)

        # TODO: make figsize a function of plot_size? What about non-square plots?
        # self.fig = plt.figure(figsize=(9, 9))

#        axx = plt.axes([0, 0.05, 0.9, 0.9])  # left, bottom, width, height
#        axx = fig.gca()
#        print('fig.dpi=',fig.dpi) # = 72

        #rwh - temp fix - Ah, error only occurs when "edges" is toggled on
        if (self.show_edge):
            try:
                self.circles(xvals,yvals, s=rvals, color=rgbas, edgecolor='black', linewidth=0.5 )
                # cell_circles = self.circles(xvals,yvals, s=rvals, color=rgbs, edgecolor='black', linewidth=0.5)
            except (ValueError):
                pass
        else:
            self.circles(xvals,yvals, s=rvals, color=rgbas  )

        # if (self.show_tracks):
        #     for key in self.trackd.keys():
        #         xtracks = self.trackd[key][:,0]
        #         ytracks = self.trackd[key][:,1]
        #         plt.plot(xtracks[0:frame],ytracks[0:frame],  linewidth=5)

        # plt.xlim(self.axes_min, self.axes_max)
        # plt.ylim(self.axes_min, self.axes_max)
        #   ax.grid(False)
#        axx.set_title(title_str)
        # plt.title(title_str)

    #---------------------------------------------------------------------------
    # assume "frame" is cell frame #, unless Cells is togggled off, then it's the substrate frame #
    # def plot_substrate(self, frame, grid):
    def plot_substrate(self, frame):
        # global current_idx, axes_max, gFileId, field_index

        # print("plot_substrate(): frame*self.substrate_delta_t  = ",frame*self.substrate_delta_t)
        # print("plot_substrate(): frame*self.svg_delta_t  = ",frame*self.svg_delta_t)
        self.title_str = ''

        # Recall:
        # self.svg_delta_t = config_tab.svg_interval.value
        # self.substrate_delta_t = config_tab.mcds_interval.value
        # self.modulo = int(self.substrate_delta_t / self.svg_delta_t)
        # self.therapy_activation_time = user_params_tab.therapy_activation_time.value

        # print("plot_substrate(): pre_therapy: max svg, substrate frames = ",max_svg_frame_pre_therapy, max_substrate_frame_pre_therapy)

        # Assume: # .svg files >= # substrate files
#        if (self.cells_toggle.value):

        # if (self.substrates_toggle.value and frame*self.substrate_delta_t <= self.svg_frame*self.svg_delta_t):
        # if (self.substrates_toggle.value and (frame % self.modulo == 0)):
        if (self.substrates_toggle.value):
            # self.fig = plt.figure(figsize=(14, 15.6))
            # self.fig = plt.figure(figsize=(15.0, 12.5))
            self.fig = plt.figure(figsize=(self.figsize_width_substrate, self.figsize_height_substrate))

            # rwh - funky way to figure out substrate frame for pc4cancerbots (due to user-defined "save_interval*")
            # self.cell_time_mins 
            # self.substrate_frame = int(frame / self.modulo)
            if (self.customized_output_freq and (frame > self.max_svg_frame_pre_therapy)):
                # max_svg_frame_pre_therapy = int(self.therapy_activation_time/self.svg_delta_t)
                # max_substrate_frame_pre_therapy = int(self.therapy_activation_time/self.substrate_delta_t)
                self.substrate_frame = self.max_substrate_frame_pre_therapy + (frame - self.max_svg_frame_pre_therapy)
            else:
                self.substrate_frame = int(frame / self.modulo)

            # print("plot_substrate(): self.substrate_frame=",self.substrate_frame)        

            # if (self.substrate_frame > (self.num_substrates-1)):
                # self.substrate_frame = self.num_substrates-1

            # print('self.substrate_frame = ',self.substrate_frame)
            # if (self.cells_toggle.value):
            #     self.modulo = int((self.num_svgs - 1) / (self.num_substrates - 1))
            #     self.substrate_frame = frame % self.modulo
            # else:
            #     self.substrate_frame = frame 
            fname = "output%08d_microenvironment0.mat" % self.substrate_frame
            xml_fname = "output%08d.xml" % self.substrate_frame
            # fullname = output_dir_str + fname

    #        fullname = fname
            full_fname = os.path.join(self.output_dir, fname)
            # print("--- plot_substrate(): full_fname=",full_fname)
            full_xml_fname = os.path.join(self.output_dir, xml_fname)
    #        self.output_dir = '.'

    #        if not os.path.isfile(fullname):
            if not os.path.isfile(full_fname):
                print("Once output files are generated, click the slider.")  # No:  output00000000_microenvironment0.mat
                return

    #        tree = ET.parse(xml_fname)
            tree = ET.parse(full_xml_fname)
            xml_root = tree.getroot()
            mins = round(int(float(xml_root.find(".//current_time").text)))  # TODO: check units = mins
            self.substrate_mins= round(int(float(xml_root.find(".//current_time").text)))  # TODO: check units = mins

            hrs = int(mins/60)
            days = int(hrs/24)
            self.title_str = 'substrate: %dd, %dh, %dm' % (int(days),(hrs%24), mins - (hrs*60))
            # self.title_str = 'substrate: %dm' % (mins )   # rwh


            info_dict = {}
    #        scipy.io.loadmat(fullname, info_dict)
            scipy.io.loadmat(full_fname, info_dict)
            M = info_dict['multiscale_microenvironment']
            #     global_field_index = int(mcds_field.value)
            #     print('plot_substrate: field_index =',field_index)
            f = M[self.field_index, :]   # 4=tumor cells field, 5=blood vessel density, 6=growth substrate
            # plt.clf()
            # my_plot = plt.imshow(f.reshape(400,400), cmap='jet', extent=[0,20, 0,20])
        
            # self.fig = plt.figure(figsize=(18.0,15))  # this strange figsize results in a ~square contour plot

            # plt.subplot(grid[0:1, 0:1])
            # main_ax = self.fig.add_subplot(grid[0:1, 0:1])  # works, but tiny upper-left region
            #main_ax = self.fig.add_subplot(grid[0:2, 0:2])
            # main_ax = self.fig.add_subplot(grid[0:, 0:2])
            #main_ax = self.fig.add_subplot(grid[:-1, 0:])   # nrows, ncols
            #main_ax = self.fig.add_subplot(grid[0:, 0:])   # nrows, ncols
            #main_ax = self.fig.add_subplot(grid[0:4, 0:])   # nrows, ncols


            # main_ax = self.fig.add_subplot(grid[0:3, 0:])   # nrows, ncols
            # main_ax = self.fig.add_subplot(111)   # nrows, ncols


            # plt.rc('font', size=10)  # TODO: does this affect the Cell plots fonts too? YES. Not what we want.

            #     fig.set_tight_layout(True)
            #     ax = plt.axes([0, 0.05, 0.9, 0.9 ]) #left, bottom, width, height
            #     ax = plt.axes([0, 0.0, 1, 1 ])
            #     cmap = plt.cm.viridis # Blues, YlOrBr, ...
            #     im = ax.imshow(f.reshape(100,100), interpolation='nearest', cmap=cmap, extent=[0,20, 0,20])
            #     ax.grid(False)

            # print("substrates.py: ------- numx, numy = ", self.numx, self.numy )
            # if (self.numx == 0):   # need to parse vals from the config.xml
            #     # print("--- plot_substrate(): full_fname=",full_fname)
            #     fname = os.path.join(self.output_dir, "config.xml")
            #     tree = ET.parse(fname)
            #     xml_root = tree.getroot()
            #     self.xmin = float(xml_root.find(".//x_min").text)
            #     self.xmax = float(xml_root.find(".//x_max").text)
            #     dx = float(xml_root.find(".//dx").text)
            #     self.ymin = float(xml_root.find(".//y_min").text)
            #     self.ymax = float(xml_root.find(".//y_max").text)
            #     dy = float(xml_root.find(".//dy").text)
            #     self.numx =  math.ceil( (self.xmax - self.xmin) / dx)
            #     self.numy =  math.ceil( (self.ymax - self.ymin) / dy)

            try:
                xgrid = M[0, :].reshape(self.numy, self.numx)
                ygrid = M[1, :].reshape(self.numy, self.numx)
            except:
                print("substrates.py: mismatched mesh size for reshape: numx,numy=",self.numx, self.numy)
                pass
#                xgrid = M[0, :].reshape(self.numy, self.numx)
#                ygrid = M[1, :].reshape(self.numy, self.numx)

            num_contours = 15
            levels = MaxNLocator(nbins=num_contours).tick_values(self.cmap_min.value, self.cmap_max.value)
            contour_ok = True
            if (self.cmap_fixed_toggle.value):
                try:
                    #substrate_plot = main_ax.contourf(xgrid, ygrid, M[self.field_index, :].reshape(self.numy, self.numx), levels=levels, extend='both', cmap=self.field_cmap.value, fontsize=self.fontsize)
                    substrate_plot = plt.contourf(xgrid, ygrid, M[self.field_index, :].reshape(self.numy, self.numx), levels=levels, extend='both', cmap=self.field_cmap.value, fontsize=self.fontsize)
                except:
                    contour_ok = False
                    # print('got error on contourf 1.')
            else:    
                try:
                    #substrate_plot = main_ax.contourf(xgrid, ygrid, M[self.field_index, :].reshape(self.numy,self.numx), num_contours, cmap=self.field_cmap.value)
                    substrate_plot = plt.contourf(xgrid, ygrid, M[self.field_index, :].reshape(self.numy,self.numx), num_contours, cmap=self.field_cmap.value)
                except:
                    contour_ok = False
                    # print('got error on contourf 2.')

            if (contour_ok):
                # main_ax.set_title(self.title_str, fontsize=self.fontsize)
                plt.title(self.title_str, fontsize=self.fontsize)
                # main_ax.tick_params(labelsize=self.fontsize)
            # cbar = plt.colorbar(my_plot)
                # cbar = self.fig.colorbar(substrate_plot, ax=main_ax)
                cbar = self.fig.colorbar(substrate_plot)
                cbar.ax.tick_params(labelsize=self.fontsize)
                # cbar = main_ax.colorbar(my_plot)
                # cbar.ax.tick_params(labelsize=self.fontsize)
            # axes_min = 0
            # axes_max = 2000

            # main_ax.set_xlim([self.xmin, self.xmax])
            # main_ax.set_ylim([self.ymin, self.ymax])
            plt.xlim(self.xmin, self.xmax)
            plt.ylim(self.ymin, self.ymax)

            # if (frame == 0):  # maybe allow substrate grid display later
            #     xs = np.linspace(self.xmin,self.xmax,self.numx)
            #     ys = np.linspace(self.ymin,self.ymax,self.numy)
            #     hlines = np.column_stack(np.broadcast_arrays(xs[0], ys, xs[-1], ys))
            #     vlines = np.column_stack(np.broadcast_arrays(xs, ys[0], xs, ys[-1]))
            #     grid_lines = np.concatenate([hlines, vlines]).reshape(-1, 2, 2)
            #     line_collection = LineCollection(grid_lines, color="gray", linewidths=0.5)
            #     # ax = main_ax.gca()
            #     main_ax.add_collection(line_collection)
            #     # ax.set_xlim(xs[0], xs[-1])
            #     # ax.set_ylim(ys[0], ys[-1])


        # Now plot the cells (possibly on top of the substrate)
        if (self.cells_toggle.value):
            if (not self.substrates_toggle.value):
                # self.fig = plt.figure(figsize=(12, 12))
                self.fig = plt.figure(figsize=(self.figsize_width_svg, self.figsize_height_svg))
            # self.plot_svg(frame)
            self.svg_frame = frame
            # print('plot_svg with frame=',self.svg_frame)
            self.plot_svg(self.svg_frame)

        # plt.subplot(grid[2, 0])
        # oxy_ax = self.fig.add_subplot(grid[2:, 0:1])
        #oxy_ax = self.fig.add_subplot(grid[:2, 2:])

        #oxy_ax = self.fig.add_subplot(grid[:-1, 0:2])  # nrows, ncols
        #oxy_ax = self.fig.add_subplot(grid[2:3, 0:1])  # nrows, ncols

        # oxy_ax = self.fig.add_subplot(grid[4:4, 0:1])  # invalid
#        main_ax = self.fig.add_subplot(grid[0:1, 0:1])

        # experiment with small plot of oxygen (or whatever)
        # oxy_ax = self.fig.add_subplot(grid[3:4, 0:1])  # nrows, ncols
        # x = np.linspace(0, 500)
        # oxy_ax.plot(x, 300*np.sin(x))

    #---------------------------------------------------------------------------
    # def plot_plots(self, frame):
    #     # if (self.first_time):
    #     #     self.svg_delta_t = 1
    #     #     self.substrate_delta_t = 1
    #     #     self.first_time = False

    #     if (self.substrates_toggle.value):
    #         self.fig = plt.figure(figsize=(14, 15.6))
    #     else:  # only cells being displayed (maybe)
    #         self.fig = plt.figure(figsize=(12, 12))
    #     # grid = plt.GridSpec(4, 3, wspace=0.10, hspace=0.2)   # (nrows, ncols)
    #     # self.plot_substrate(frame, grid)
    #     self.plot_substrate(frame)
    #     # self.plot_svg(frame)

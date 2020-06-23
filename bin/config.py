# Config Tab

import os
from ipywidgets import Layout, Label, Text, Checkbox, Button, HBox, VBox, \
    FloatText, BoundedIntText, BoundedFloatText, HTMLMath, Dropdown


class ConfigTab(object):

    def __init__(self):
        
#        micron_units = HTMLMath(value=r"$\mu M$")
        micron_units = Label('micron')   # use "option m" (Mac, for micro symbol)
#        micron_units = Label('microns')   # use "option m" (Mac, for micro symbol)

        constWidth = '180px'
        # tab_height = '400px'
        tab_height = '500px'
#        tab_layout = Layout(width='900px',   # border='2px solid black',
#        tab_layout = Layout(width='850px',   # border='2px solid black',
#                            height=tab_height, overflow_y='scroll',)
#        np_tab_layout = Layout(width='800px',  # border='2px solid black',
#                               height='350px', overflow_y='scroll',)

        # my_domain = [0,0,-10, 2000,2000,10, 20,20,20]  # [x,y,zmin,  x,y,zmax, x,y,zdelta]
#        label_domain = Label('Domain ($\mu M$):')
        label_domain = Label('Domain (micron):')
        stepsize = 10
        disable_domain = False
        self.xmin = FloatText(step=stepsize,
            # description='$X_{min}$',
            description='Xmin',
            disabled = disable_domain,
            layout=Layout(width=constWidth),
        )
        self.ymin = FloatText(step=stepsize,
            description='Ymin',
            disabled = disable_domain,
            layout=Layout(width=constWidth),
        )
        self.zmin = FloatText(step=stepsize,
            description='Zmin',
            disabled = disable_domain,
            layout=Layout(width=constWidth),
        )
        self.xmax = FloatText(step=stepsize,
            description='Xmax',
            disabled = disable_domain,
            layout=Layout(width=constWidth),
        )
        self.ymax = FloatText(step=stepsize,
            description='Ymax',
            disabled = disable_domain,
            layout=Layout(width=constWidth),
        )
        self.zmax = FloatText(step=stepsize,
            description='Zmax',
            disabled = disable_domain,
            layout=Layout(width=constWidth),
        )
#            description='$Time_{max}$',
        self.tmax = BoundedFloatText(
            min=0.,
            max=100000000,
            step=stepsize,
            description='Max Time',
            layout=Layout(width=constWidth),
        )
        self.xdelta = BoundedFloatText(
            min=1.,
            description='dx',   # '∆x',  # Mac: opt-j for delta
            disabled = disable_domain,
            layout=Layout(width=constWidth),
        )
        self.ydelta = BoundedFloatText(
            min=1.,
            description='dy',
            disabled = disable_domain,
            layout=Layout(width=constWidth),
        )
        self.zdelta = BoundedFloatText(
            min=1.,
            description='dz',
            disabled = disable_domain,
            layout=Layout(width=constWidth),
        )
        """
        self.tdelta = BoundedFloatText(
            min=0.01,
            description='$Time_{delta}$',
            layout=Layout(width=constWidth),
        )
        """

        """
        self.toggle2D = Checkbox(
            description='2-D',
            layout=Layout(width=constWidth),
        )
        def toggle2D_cb(b):
            if (self.toggle2D.value):
                #zmin.disabled = zmax.disabled = zdelta.disabled = True
                zmin.disabled = True
                zmax.disabled = True
                zdelta.disabled = True
            else:
                zmin.disabled = False
                zmax.disabled = False
                zdelta.disabled = False
            
        self.toggle2D.observe(toggle2D_cb)
        """

        x_row = HBox([self.xmin, self.xmax, self.xdelta])
        y_row = HBox([self.ymin, self.ymax, self.ydelta])
        z_row = HBox([self.zmin, self.zmax, self.zdelta])

        self.omp_threads = BoundedIntText(
            min=1,
            max=4,
            description='# threads',
            layout=Layout(width=constWidth),
        )

        # self.toggle_prng = Checkbox(
        #     description='Seed PRNG', style={'description_width': 'initial'},  # e.g. 'initial'  '120px'
        #     layout=Layout(width=constWidth),
        # )
        # self.prng_seed = BoundedIntText(
        #     min = 1,
        #     description='Seed', 
        #     disabled=True,
        #     layout=Layout(width=constWidth),
        # )
        # def toggle_prng_cb(b):
        #     if (toggle_prng.value):
        #         self.prng_seed.disabled = False
        #     else:
        #         self.prng_seed.disabled = True
            
        # self.toggle_prng.observe(toggle_prng_cb)
        #prng_row = HBox([toggle_prng, prng_seed])

        self.toggle_svg = Checkbox(
            description='Cells',    # SVG
            layout=Layout(width='150px') )  # constWidth = '180px'
        # self.svg_t0 = BoundedFloatText (
        #     min=0,
        #     description='$T_0$',
        #     layout=Layout(width=constWidth),
        # )
        self.svg_interval = BoundedFloatText(
            min=0.001,
            max=99999999,   # TODO: set max on all Bounded to avoid unwanted default
            description='every',
            layout=Layout(width='160px'),
        )
        self.mcds_interval = BoundedFloatText(
            min=0.001,
            max=99999999,
            description='every',
#            disabled=True,
            layout=Layout(width='160px'),
        )

        # don't let this be > mcds interval
        def svg_interval_cb(b):
            if (self.svg_interval.value > self.mcds_interval.value):
                self.svg_interval.value = self.mcds_interval.value

        self.svg_interval.observe(svg_interval_cb)  # BEWARE: when fill_gui, this sets value = 1 !

        # don't let this be < svg interval
        def mcds_interval_cb(b):
            if (self.mcds_interval.value < self.svg_interval.value):
                self.mcds_interval.value = self.svg_interval.value

        self.mcds_interval.observe(mcds_interval_cb)   # BEWARE: see warning above

        def toggle_svg_cb(b):
            if (self.toggle_svg.value):
                # self.svg_t0.disabled = False 
                self.svg_interval.disabled = False
            else:
                # self.svg_t0.disabled = True
                self.svg_interval.disabled = True
            
        self.toggle_svg.observe(toggle_svg_cb)


        self.toggle_mcds = Checkbox(
        #     value=False,
            description='Subtrates',   # Full
            layout=Layout(width='180px'),
        )
        # self.mcds_t0 = FloatText(
        #     description='$T_0$',
        #     disabled=True,
        #     layout=Layout(width=constWidth),
        # )
        def toggle_mcds_cb(b):
            if (self.toggle_mcds.value):
                # self.mcds_t0.disabled = False #False
                self.mcds_interval.disabled = False
            else:
                # self.mcds_t0.disabled = True
                self.mcds_interval.disabled = True
            
        self.toggle_mcds.observe(toggle_mcds_cb)
       
        svg_mat_output_row = HBox([Label('Plots:'),self.toggle_svg, HBox([self.svg_interval,Label('min')]), 
            self.toggle_mcds, HBox([self.mcds_interval,Label('min')])  ])

        # to sync, do this
        # svg_mat_output_row = HBox( [Label('Plots:'), self.svg_interval, Label('min')]) 

        #write_config_row = HBox([write_config_button, write_config_file])
        #run_sim_row = HBox([run_button, run_command_str, kill_button])
        # run_sim_row = HBox([run_button, run_command_str])
        # run_sim_row = HBox([run_button.w])  # need ".w" for the custom RunCommand widget

        label_blankline = Label('')
        # toggle_2D_seed_row = HBox([toggle_prng, prng_seed])  # toggle2D


        box_layout = Layout(border='1px solid')
#        domain_box = VBox([label_domain,x_row,y_row,z_row], layout=box_layout)
        domain_box = VBox([label_domain,x_row,y_row], layout=box_layout)
        self.tab = VBox([domain_box,
#                         label_blankline, 
                         HBox([self.tmax, Label('min')]), self.omp_threads,  
                         svg_mat_output_row,
#                         HBox([self.substrate[3], self.diffusion_coef[3], self.decay_rate[3] ]),
                         ])  # output_dir, toggle_2D_seed_
#                         ], layout=tab_layout)  # output_dir, toggle_2D_seed_

    # Populate the GUI widgets with values from the XML
    def fill_gui(self, xml_root):
        self.xmin.value = float(xml_root.find(".//x_min").text)
        self.xmax.value = float(xml_root.find(".//x_max").text)
        self.xdelta.value = float(xml_root.find(".//dx").text)
    
        self.ymin.value = float(xml_root.find(".//y_min").text)
        self.ymax.value = float(xml_root.find(".//y_max").text)
        self.ydelta.value = float(xml_root.find(".//dy").text)
    
        self.zmin.value = float(xml_root.find(".//z_min").text)
        self.zmax.value = float(xml_root.find(".//z_max").text)
        self.zdelta.value = float(xml_root.find(".//dz").text)
        
        self.tmax.value = float(xml_root.find(".//max_time").text)
        
        self.omp_threads.value = int(xml_root.find(".//omp_num_threads").text)
        
        if xml_root.find(".//full_data//enable").text.lower() == 'true':
            self.toggle_mcds.value = True
        else:
            self.toggle_mcds.value = False
        self.mcds_interval.value = float(xml_root.find(".//full_data//interval").text)

        # NOTE: do this *after* filling the mcds_interval, directly above, due to the callback/constraints on them
        if xml_root.find(".//SVG//enable").text.lower() == 'true':
            self.toggle_svg.value = True
        else:
            self.toggle_svg.value = False
        self.svg_interval.value = float(xml_root.find(".//SVG//interval").text)


    # Read values from the GUI widgets and generate/write a new XML
    def fill_xml(self, xml_root):
        # print('config.py fill_xml() !!!!!')
        # TODO: verify template .xml file exists!

        # TODO: verify valid type (numeric) and range?
        xml_root.find(".//x_min").text = str(self.xmin.value)
        xml_root.find(".//x_max").text = str(self.xmax.value)
        xml_root.find(".//dx").text = str(self.xdelta.value)
        xml_root.find(".//y_min").text = str(self.ymin.value)
        xml_root.find(".//y_max").text = str(self.ymax.value)
        xml_root.find(".//dy").text = str(self.ydelta.value)
        xml_root.find(".//z_min").text = str(self.zmin.value)
        xml_root.find(".//z_max").text = str(self.zmax.value)
        xml_root.find(".//dz").text = str(self.zdelta.value)

        xml_root.find(".//max_time").text = str(self.tmax.value)

        xml_root.find(".//omp_num_threads").text = str(self.omp_threads.value)

        xml_root.find(".//SVG").find(".//enable").text = str(self.toggle_svg.value)
        xml_root.find(".//SVG").find(".//interval").text = str(self.svg_interval.value)
        xml_root.find(".//full_data").find(".//enable").text = str(self.toggle_mcds.value)
        xml_root.find(".//full_data").find(".//interval").text = str(self.mcds_interval.value)

        #    user_details = ET.SubElement(root, "user_details")
        #    ET.SubElement(user_details, "PhysiCell_settings", name="version").text = "devel-version"
        #    ET.SubElement(user_details, "domain")
        #    ET.SubElement(user_details, "xmin").text = "-100"

        #    tree = ET.ElementTree(root)
        #    tree.write(write_config_file.value)
        #    tree.write("test.xml")

        # TODO: verify can write to this filename
#        tree.write(write_config_file.value)

    def get_num_svg_frames(self):
        if (self.toggle_svg.value):
            return int(self.tmax.value/self.svg_interval.value)
        else:
            return 0

    def get_num_substrate_frames(self):
        if (self.toggle_mcds.value):
            return int(self.tmax.value/self.mcds_interval.value)
        else:
            return 0

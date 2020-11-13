# populations  Tab

import os

from ipywidgets import HBox, interactive
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np
import scipy.io
import xml.etree.ElementTree as ET
import glob
import warnings

#warnings.warn(message, mplDeprecation, stacklevel=1)
warnings.filterwarnings("ignore")

class PopulationsTab(object):

    def __init__(self):
        
        self.output_dir = '.'

        self.figsize_width = 15.0
        self.figsize_height = 8

        config_file = "data/PhysiCell_settings.xml"

        self.cell_lines = {}
        self.full_data_interval = 0
        self.full_data_units = "min"
        self.pop_counts = None
        self.list_colors = rcParams["axes.prop_cycle"].by_key()["color"]
        self.palette = {}

        if os.path.isfile(config_file):

            try:
                tree = ET.parse(config_file)
            except:
                print("Cannot parse", config_file, "- check it's XML syntax.")
                return

            root = tree.getroot()
            uep = root.find('.//cell_definitions')  # find unique entry point (uep)
            for child in uep.findall('cell_definition'):
                self.cell_lines[int(child.attrib["ID"])] = child.attrib["name"]

            uep = root.find('.//save/full_data/interval')
            raw_interval = uep.text
            units = uep.attrib['units']
            if units == "min":
                self.full_data_interval = int(raw_interval)
            elif units == "hour":
                self.full_data_interval = int(raw_interval)*60

        self.max_frames = 0
        self.pop_plot = interactive(self.plot_celltypes, frame=(0, self.max_frames), stacked=True, continuous_update=False)

        self.tab = HBox([self.pop_plot])

    def update(self, rdir=''):
        if rdir:
            self.output_dir = rdir

        all_files = sorted(glob.glob(os.path.join(self.output_dir, 'output*_cells_physicell.mat')))
        if len(all_files) > 0:
            last_file = all_files[-1]
            self.max_frames = int(last_file[-28:-20])  # assumes naming scheme: "output%08d_cells_physicell.mat"
            self.pop_plot.children[0].max = self.max_frames

    def plot_celltypes(self, frame=None, stacked=True):

        if frame <= 0:
            return

        for i in range(0, frame+1):

            if self.pop_counts is None or self.pop_counts.shape[1] <= i:

                fname = "output%08d_cells_physicell.mat" % i
                full_fname = os.path.join(self.output_dir, fname)

                if not os.path.isfile(full_fname):
                    print("Once output files are generated, click the slider.")
                    return

                info_dict = {}
                scipy.io.loadmat(full_fname, info_dict)

                M = info_dict['cells'][5, :].astype(int)

                unique, counts = np.unique(M, return_counts=True)

                pop_count = np.zeros((len(self.cell_lines), 1))
                pop_count[unique, 0] = counts

                if i == 0:
                    self.pop_counts = pop_count

                else:
                    self.pop_counts = np.append(self.pop_counts, pop_count, axis=1)

        t_data = []
        y_max = 0
        t_names = []

        for t_id, name in self.cell_lines.items():
            if self.pop_counts[t_id, 0:frame+1].any():
                y_max = max(y_max, np.max(self.pop_counts[t_id, 0:frame+1]))
                t_data.append(self.pop_counts[t_id, 0:frame+1])
                t_names.append(name)
                if name not in self.palette.keys():
                    self.palette.update({name: self.list_colors[len(self.palette.keys()) % 10]})

        color_list = [self.palette[t_name] for t_name in t_names]

        t_times = np.array(range(0, frame+1))
        t_times = t_times * self.full_data_interval
        t_unit = self.full_data_units

        if np.max(t_times) > 1000:
            if t_unit == "min":
                t_times = t_times / 60
                t_unit = "hour"

            elif t_unit == "hour":
                t_times = t_times / 24
                t_unit = "day"

        fig = plt.figure(figsize=(self.figsize_width, self.figsize_height))
        ax = fig.add_subplot(111)

        if stacked:
            ax.stackplot(
                t_times,
                t_data,
                labels=t_names,
                colors=color_list
            )
        else:
            for t_datum, t_label in zip(t_data, t_names):
                ax.plot(
                    t_times,
                    t_datum,
                    label=t_label,
                    color=self.palette[t_label]
                    
                )
            ax.set_ylim(0, y_max*1.1)
            
        ax.legend(labels=t_names, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4)
        ax.margins(0, 0)    # Set margins to avoid "whitespace"
        ax.set_xlabel("Time (" + t_unit + "s)")
        ax.set_ylabel("Population size (cells)")

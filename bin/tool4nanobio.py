import ipywidgets as widgets
import xml.etree.ElementTree as ET  # https://docs.python.org/2/library/xml.etree.elementtree.html
import os
import glob
import shutil
import math
import datetime
import tempfile
from about import AboutTab
from config import ConfigTab
from microenv_params import MicroenvTab
from user_params import UserTab
try:
    from cell_types import CellTypesTab
except:
    # print("cell_types.py does not exist due to no <cell_definitions>")
    pass
# from svg import SVGTab
from substrates import SubstrateTab
from animate_tab import AnimateTab
from pathlib import Path
import platform
import subprocess
from debug import debug_view

hublib_flag = True
if platform.system() != 'Windows':
    try:
#        print("Trying to import hublib.ui")
        from hublib.ui import RunCommand, Submit
        # from hublib2.ui import RunCommand, Submit
    except:
        hublib_flag = False
else:
    hublib_flag = False


# join_our_list = "(Join/ask questions at https://groups.google.com/forum/#!forum/physicell-users)\n"


# create the tabs, but don't display yet
about_tab = AboutTab()
config_tab = ConfigTab()

xml_file = os.path.join('data', 'PhysiCell_settings.xml')
full_xml_filename = os.path.abspath(xml_file)

tree = ET.parse(full_xml_filename)  # this file cannot be overwritten; part of tool distro
xml_root = tree.getroot()

microenv_tab = MicroenvTab()
user_tab = UserTab()

if xml_root.find('.//cell_definitions'):
    cell_types_tab = CellTypesTab()

# svg = SVGTab()
sub = SubstrateTab()
animate_tab = AnimateTab()

nanoHUB_flag = False
if( 'HOME' in os.environ.keys() ):
    nanoHUB_flag = "home/nanohub" in os.environ['HOME']


# callback when user selects a cached run in the 'Load Config' dropdown widget.
# HOWEVER, beware if/when this is called after a sim finishes and the Load Config dropdown widget reverts to 'DEFAULT'.
# In that case, we don't want to recompute substrate.py self.numx, self.numy because we're still displaying plots from previous sim.
def read_config_cb(_b):
    # with debug_view:
    #     print("read_config_cb", read_config.value)

    sub.first_time = True

    if read_config.value is None:  #occurs when a Run just finishes and we update pulldown with the new cache dir??
        # with debug_view:
        #     print("NOTE: read_config_cb(): No read_config.value. Returning!")
        # print("NOTE: read_config_cb(): No read_config.value. Returning!")
        return

    if os.path.isdir(read_config.value):
        is_dir = True
        config_file = os.path.join(read_config.value, 'config.xml')
        # print("read_config_cb(): is_dir=True; config_file=",config_file)
    else:
        is_dir = False
        config_file = read_config.value
        # print("read_config_cb(): is_dir=False; --- config_file=",config_file)

    if Path(config_file).is_file():
        # with debug_view:
        # print("read_config_cb():  calling fill_gui_params with ",config_file)
        fill_gui_params(config_file)  #should verify file exists!

        # If cells or substrates toggled off in Config tab, toggle off in Plots tab
        if config_tab.toggle_svg.value == False:
            sub.cells_toggle.value = False
            sub.cells_toggle.disabled = True
        else:
            sub.cells_toggle.disabled = False

        if config_tab.toggle_mcds.value == False:
            sub.substrates_toggle.value = False
            sub.substrates_toggle.disabled = True
        else:
            sub.substrates_toggle.disabled = False

    else:
        # with debug_view:
        #     print("read_config_cb: ",config_file, " does not exist.")
        return
    
    # update visualization tabs
    if is_dir:
        # svg.update(read_config.value)
        # print("read_config_cb():  is_dir True, calling update_params")
        sub.update_params(config_tab, user_tab)
        sub.update(read_config.value)
    # else:  # may want to distinguish "DEFAULT" from other saved .xml config files
        # FIXME: really need a call to clear the visualizations
        # svg.update('')
        # sub.update('')
        # print("read_config_cb():  is_dir False, calling update_params")
        # sub.update_params(config_tab)
        # print("read_config_cb():  is_dir False, calling sub.update()")
        # sub.update()  # NOTE: even if we attempt this, it doesn't really refresh the plots
        # pass
        

# Using the param values in the GUI, write a new .xml config file
def write_config_file(name):
    # with debug_view:
    #     print("write_config_file: based on ",full_filename)
    tree = ET.parse(full_xml_filename)  # this file cannot be overwritten; part of tool distro
    xml_root = tree.getroot()
    config_tab.fill_xml(xml_root)
    microenv_tab.fill_xml(xml_root)
    user_tab.fill_xml(xml_root)
    tree.write(name)

    # update substrate mesh layout (beware of https://docs.python.org/3/library/functions.html#round)
    sub.update_params(config_tab, user_tab)
    # sub.numx =  math.ceil( (config_tab.xmax.value - config_tab.xmin.value) / config_tab.xdelta.value )
    # sub.numy =  math.ceil( (config_tab.ymax.value - config_tab.ymin.value) / config_tab.ydelta.value )
    # print("tool4nanobio.py: ------- sub.numx, sub.numy = ", sub.numx, sub.numy)


# callback from write_config_button
# def write_config_file_cb(b):
#     path_to_share = os.path.join('~', '.local','share','tool4nanobio')
#     dirname = os.path.expanduser(path_to_share)

#     val = write_config_box.value
#     if val == '':
#         val = write_config_box.placeholder
#     name = os.path.join(dirname, val)
#     write_config_file(name)


# Fill the "Load Config" dropdown widget with valid cached results (and 
# default & previous config options)
def get_config_files():
    cf = {'DEFAULT': full_xml_filename}
    path_to_share = os.path.join('~', '.local','share','tool4nanobio')
    dirname = os.path.expanduser(path_to_share)
    try:
        os.makedirs(dirname)
    except:
        pass
    files = glob.glob("%s/*.xml" % dirname)
    # dict.update() will append any new (key,value) pairs
    cf.update(dict(zip(list(map(os.path.basename, files)), files)))

    # Find the dir path (full_path) to the cached dirs
    if nanoHUB_flag:
        full_path = os.path.expanduser("~/data/results/.submit_cache/tool4nanobio")  # does Windows like this?
    else:
        # local cache
        try:
            cachedir = os.environ['CACHEDIR']
            full_path = os.path.join(cachedir, "tool4nanobio")
        except:
            # print("Exception in get_config_files")
            return cf

    # Put all those cached (full) dirs into a list
    dirs_all = [os.path.join(full_path, f) for f in os.listdir(full_path) if f != '.cache_table']

    # Only want those dirs that contain output files (.svg, .mat, etc), i.e., handle the
    # situation where a user cancels a Run before it really begins, which may create a (mostly) empty cached dir.
    dirs = [f for f in dirs_all if len(os.listdir(f)) > 5]   # "5" somewhat arbitrary
    # with debug_view:
    #     print(dirs)

    # Get a list of sorted dirs, according to creation timestamp (newest -> oldest)
    sorted_dirs = sorted(dirs, key=os.path.getctime, reverse=True)
    # with debug_view:
    #     print(sorted_dirs)

    # Get a list of timestamps associated with each dir
    sorted_dirs_dates = [str(datetime.datetime.fromtimestamp(os.path.getctime(x))) for x in sorted_dirs]
    # Create a dict of {timestamp:dir} pairs
    cached_file_dict = dict(zip(sorted_dirs_dates, sorted_dirs))
    cf.update(cached_file_dict)
    # with debug_view:
    #     print(cf)
    return cf


# Using params in a config (.xml) file, fill GUI widget values in each of the "input" tabs
def fill_gui_params(config_file):
    # with debug_view:
    #     print("fill_gui_params: filling with ",config_file)
    # print("fill_gui_params: filling with ",config_file)
    tree = ET.parse(config_file)
    xml_root = tree.getroot()
    config_tab.fill_gui(xml_root)
    microenv_tab.fill_gui(xml_root)
    user_tab.fill_gui(xml_root)


def run_done_func(s, rdir):
    # with debug_view:
    #     print('run_done_func: results in', rdir)
    
    if nanoHUB_flag:
        # Email the user that their job has completed
        os.system("submit  mail2self -s 'nanoHUB tool4nanobio' -t 'Your Run completed.'&")

    # save the config file to the cache directory
    shutil.copy('config.xml', rdir)

    # cd out of tmpdir 
    os.chdir(homedir)

    # new results are available, so update dropdown
    # with debug_view:
    #     print('run_done_func: ---- before updating read_config.options')
    read_config.options = get_config_files()
    # with debug_view:
    #     print('run_done_func: ---- after updating read_config.options')

    # sub.update_dropdown_fields("data")   # WARNING: fill in the substrate field(s)

    # and update visualizations
    # svg.update(rdir)
    sub.update(rdir)

    animate_tab.gen_button.disabled = False

    # with debug_view:
    #     print('RDF DONE')


# This is used now for the ("smart") RunCommand
def run_sim_func(s):
    # with debug_view:
    #     print('run_sim_func')

    animate_tab.gen_button.disabled = True

    # If cells or substrates toggled off in Config tab, toggle off in Plots tab
    if config_tab.toggle_svg.value == False:
        sub.cells_toggle.value = False
        sub.cells_toggle.disabled = True
    else:
        sub.cells_toggle.disabled = False
    if config_tab.toggle_mcds.value == False:
        sub.substrates_toggle.value = False
        sub.substrates_toggle.disabled = True
    else:
        sub.substrates_toggle.disabled = False

    # make sure we are where we started
    os.chdir(homedir)

    # remove any previous data
    # NOTE: this dir name needs to match the <folder>  in /data/<config_file.xml>
    os.system('rm -rf tmpdir*')
    if os.path.isdir('tmpdir'):
        # something on NFS causing issues...
        tname = tempfile.mkdtemp(suffix='.bak', prefix='tmpdir_', dir='.')
        shutil.move('tmpdir', tname)
    os.makedirs('tmpdir')

    # write the default config file to tmpdir
    new_config_file = "tmpdir/config.xml"  # use Path; work on Windows?
    write_config_file(new_config_file)  

    with open(new_config_file) as f:
        run_name = s.make_rname(f.read())

    tdir = os.path.abspath('tmpdir')
    os.chdir(tdir)  # operate from tmpdir; temporary output goes here.  may be copied to cache later
    # svg.update(tdir)
    # sub.update_params(config_tab)
    sub.update(tdir)
    # animate_tab.update(tdir)

    if nanoHUB_flag:
        if remote_cb.value:
            s.run(run_name, "-v ncn-hub_M@brown -n 8 -w 1440 tool4nanobio-r7 config.xml")   # "-r7" suffix??
        else:
            # read_config.index = 0   # reset Dropdown 'Load Config' to 'DEFAULT' when Run interactively
            s.run(run_name, "--local ../bin/myproj config.xml")
    else:
        # reset Dropdown 'Load Config' to 'DEFAULT' when Run interactively
        # Warning: this will trigger read_config_cb() !!
        # read_config.index = 0   
        s.run("../bin/myproj config.xml", runname=run_name)

    # with debug_view:
    #     print('run_sim_func DONE')


def outcb(s):
    # This is called when new output is received.
    # Only update file list for certain messages: 
    # print("outcb(): s=",s)
    if "simulat" in s:    # "current simulated time: 60 min (max: 14400 min)"
        # New Data. update visualizations
        # svg.update('')
        # sub.update('')
        # sub.update_params(config_tab)
        sub.update()
    return s


# Callback for the ("dumb") 'Run' button (without hublib.ui)
def run_button_cb(s):
#    with debug_view:
#        print('run_button_cb')

#    new_config_file = full_xml_filename
    # print("new_config_file = ", new_config_file)
#    write_config_file(new_config_file)

    # make sure we are where we started
    os.chdir(homedir)

    # remove any previous data
    # NOTE: this dir name needs to match the <folder>  in /data/<config_file.xml>
    os.system('rm -rf tmpdir*')
    if os.path.isdir('tmpdir'):
        # something on NFS causing issues...
        tname = tempfile.mkdtemp(suffix='.bak', prefix='tmpdir_', dir='.')
        shutil.move('tmpdir', tname)
    os.makedirs('tmpdir')

    # write the default config file to tmpdir
    new_config_file = "tmpdir/config.xml"  # use Path; work on Windows?
    write_config_file(new_config_file)  

    tdir = os.path.abspath('tmpdir')
    os.chdir(tdir)  # operate from tmpdir; temporary output goes here.  may be copied to cache later
    # svg.update(tdir)
    # sub.update_params(config_tab)
    sub.update(tdir)

    subprocess.Popen(["../bin/myproj", "config.xml"])


#-------------------------------------------------
if nanoHUB_flag:
    run_button = Submit(label='Run',
                       start_func=run_sim_func,
                        done_func=run_done_func,
                        cachename='tool4nanobio',
                        showcache=False,
                        outcb=outcb)
else:
    if (hublib_flag):
        run_button = RunCommand(start_func=run_sim_func,
                            done_func=run_done_func,
                            cachename='tool4nanobio',
                            showcache=False,
                            outcb=outcb)  
    else:
        run_button = widgets.Button(
            description='Run',
            button_style='success',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Run a simulation',
        )
        run_button.on_click(run_button_cb)


if nanoHUB_flag or hublib_flag:
    read_config = widgets.Dropdown(
        description='Load Config',
        options=get_config_files(),
        tooltip='Config File or Previous Run',
    )
    read_config.style = {'description_width': '%sch' % str(len(read_config.description) + 1)}
    read_config.observe(read_config_cb, names='value') 

tab_height = 'auto'
tab_layout = widgets.Layout(width='auto',height=tab_height, overflow_y='scroll',)   # border='2px solid black',

if xml_root.find('.//cell_definitions'):
    titles = ['About', 'Config Basics', 'Microenvironment', 'User Params', 'Cell Types', 'Out: Plots', 'Animate']
    tabs = widgets.Tab(children=[about_tab.tab, config_tab.tab, microenv_tab.tab, user_tab.tab, cell_types_tab.tab, sub.tab, animate_tab.tab],
                   _titles={i: t for i, t in enumerate(titles)},
                   layout=tab_layout)
else:
    titles = ['About', 'Config Basics', 'Microenvironment', 'User Params', 'Out: Plots', 'Animate']
    tabs = widgets.Tab(children=[about_tab.tab, config_tab.tab, microenv_tab.tab, user_tab.tab, sub.tab, animate_tab.tab],
                   _titles={i: t for i, t in enumerate(titles)},
                   layout=tab_layout)

homedir = os.getcwd()

tool_title = widgets.Label(r'\(\textbf{tool4nanobio}\)')
if nanoHUB_flag or hublib_flag:
    # define this, but don't use (yet)
    remote_cb = widgets.Checkbox(indent=False, value=False, description='Submit as Batch Job to Clusters/Grid')

    top_row = widgets.HBox(children=[read_config, tool_title])
    gui = widgets.VBox(children=[top_row, tabs, run_button.w])
    fill_gui_params(read_config.options['DEFAULT'])
else:
    top_row = widgets.HBox(children=[tool_title])
    gui = widgets.VBox(children=[top_row, tabs, run_button])
    fill_gui_params("data/PhysiCell_settings.xml")


# pass in (relative) directory where output data is located
output_dir = "tmpdir"
# svg.update(output_dir)

sub.update_dropdown_fields("data")   # WARNING: generates multiple "<Figure size...>" stdout!
# animate_tab.update_dropdown_fields("data")   

# print('config_tab.svg_interval.value= ',config_tab.svg_interval.value )
# print('config_tab.mcds_interval.value= ',config_tab.mcds_interval.value )
#sub.update_params(config_tab)

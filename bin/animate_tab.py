from ipywidgets import Button, Label, BoundedIntText, HBox, VBox, Output, HTML, Layout
from IPython.display import display
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import os
import glob
import subprocess
import time
import platform
import zipfile
import shutil
from pathlib import Path

hublib_flag = True
if platform.system() != 'Windows':
    try:
#        print("Trying to import hublib.ui")
        from hublib.ui import Download
    except:
        hublib_flag = False
else:
    hublib_flag = False

# hublib_flag = False   # shared testing

class AnimateTab(object):

    def __init__(self):
        self.mp4_zip_file = "cells_mp4.zip"
        self.mp4_file = "cells.mp4"

        self.instructions = Label("After a simulation completes, generate a video of cells (from SVG files). Does not work for cached results yet.")
        self.feedback = Label("                            ")
        # self.feedback.value = "Converting all svg to jpg..."

        self.gen_button = Button(
            description='Generate video',
            button_style='success',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Generate a MP4 video of cells',
        )
        self.gen_button.disabled = True
        self.gen_button.on_click(self.gen_button_cb)

        fps_style = {'description_width': '35%'}
        fps_layout = {'width': '85px'}
        # tooltip='frames per sec',  -- tooltip not available for *Text !
        self.fps = BoundedIntText(description="fps=", value=5, min=1, max=30, step=1, 
          style=fps_style, layout=fps_layout)

        size_style = {'description_width': '50%'}
        size_layout = {'width': '150px'}
        self.size = BoundedIntText(description="w,h(pixels)=", value=500, min=250, max=1500, step=10, disabled=False, tooltip='width, height of video',
          style=size_style, layout=size_layout)

        self.video = HTML( value="",
            placeholder='',
            description='',
            layout= Layout(visibility='hidden')
        )

        if (hublib_flag):
            self.download_mp4_button = Download(self.mp4_zip_file, style='success', icon='cloud-download', 
                                                tooltip='Download mp4 (you need to allow pop-ups in your browser)')
            self.download_mp4_button.w.disabled = True

            self.tab = VBox([self.instructions, HBox([ self.gen_button, self.fps, self.size, self.feedback,
                self.download_mp4_button.w]), self.video])
        else:
            self.tab = VBox([self.instructions, HBox([self.gen_button, self.fps, self.size, self.feedback]), self.video])

    #---------------------------
    # callback for the 'Generate video' button
    def gen_button_cb(self, b):

        if shutil.which('ffmpeg') is None:
            self.feedback.value = 'Error: the program "ffmpeg" cannot be found in your PATH.'
            return

        self.gen_button.description = 'working'
        self.gen_button.button_style = 'warning' # 'success','info','warning','danger' or ''
        self.gen_button.disabled = True

        self.fps.disabled = True
        self.size.disabled = True

        feedback_base = "Converting all svg to jpg..."
        self.feedback.value = feedback_base
        cwd = os.getcwd()
        if not 'tmpdir' in cwd:
            tdir = os.path.abspath('tmpdir')
            os.chdir(tdir)

        num_svg = len(glob.glob('snap*.svg'))
        idx_start = 0
        idx_end = num_svg
        for idx in range(idx_start,idx_end):   # perhaps allow stepsize > 1
            fname = "snapshot%08d" % idx
            svg_file = fname + ".svg"
            jpg_file = fname + ".jpg"
            subprocess.Popen(["convert", svg_file, jpg_file])

        delay = 2  # secs
        for idx in range(num_svg):
            num_jpg = len(glob.glob('snap*.jpg'))
            self.feedback.value = feedback_base + str(num_jpg) + " of " + str(num_svg)
            time.sleep(delay)
            if num_jpg == num_svg:
                break

        img_width = self.size.value
        if (img_width % 2):   # req divisible by 2
            img_width += 1
        img_height = img_width + 36
        try:
            os.remove(self.mp4_file)
        except OSError:
            pass
        cmd = 'ffmpeg -framerate ' + str(self.fps.value) + ' -i snapshot%08d.jpg -vf scale=' + str(img_width) + ':' + str(img_height) + ' ' + self.mp4_file

        self.feedback.value = "Converting all jpg to mp4..."
        os.system(cmd)
        

        self.gen_button.description = 'Generate'
        self.gen_button.button_style = 'success'

        self.gen_button.disabled = False
        self.fps.disabled = False
        self.size.disabled = False

        zipfile.ZipFile(self.mp4_zip_file, mode='w').write(self.mp4_file)
        try:
            os.remove(os.path.join('..', self.mp4_zip_file))
        except OSError:
            pass
        shutil.move(self.mp4_zip_file, "..")
        self.download_mp4_button.w.disabled = False

        self.feedback.value = "Done. (Wait for animation to appear below)"

        # Generate/display the animation of jpgs
        plt.ioff()
        self.fig = plt.figure(figsize= [13, 13])
        # print("------ gen_button_cb")
        self.anim_imgs = []
        fname = self.mp4_file
        # for idx in range(0,19,3):
        success = True
        for idx in range(num_jpg):
            fname = 'snapshot%08d.jpg' % idx
            # fname = 'img%08d.jpg' % idx
            # print(fname)
            try:
                img = Image.open(fname)
            except:
                self.feedback.value = "Error: cannot open " + fname
                success = False
                break
            img.thumbnail((700, 700), Image.ANTIALIAS)
            im = plt.imshow(img, animated=True)
            self.anim_imgs.append([im])
        if success:
            self.mpl_anim = animation.ArtistAnimation(self.fig, self.anim_imgs, interval=500, blit=True, repeat_delay=1000)
            self.video.value = self.mpl_anim.to_html5_video()
            self.video.layout.visibility = None
            self.feedback.value = "Done."
        plt.close(self.fig)

import contextlib
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import requests
from itertools import cycle
import time
import backend
# Multiprocessing Queue for thread data passthrough
from multiprocessing import Queue
global top_queue, bottom_queue
top_queue = Queue()
bottom_queue = Queue()

class ImageLabel(tk.Label):
    """
    A Label that displays images, and plays them if they are gifs
    :im: A PIL Image instance or a string filename
    """
    def copy_current(self,url):
       backend.clipboard(url)
       backend.notify("Image link copied successfully to clipboard")
    def load(self, url, tag , width, bgcolor):
        self.tag, self.width, self.bgcolor = tag, width, bgcolor
        LOADING = tk.PhotoImage(
                file=backend.load_resource("resources/Loading.png"))
        #create instance variable
        self.url = url
        #prepare the label to have the background of its parent widget
        self.configure(image=LOADING)

        request = requests.get(url, stream=True).raw
        try: 
            im = Image.open(request)
        except Exception:
            im = Image.open(backend.load_resource("resources/NoFile.gif"))
            
        self.framerate = 1000 / im.info['duration'] # reads the duration value and sets the framerate accordingly
        print(f"<IMAGE_HANDLER> Decoded new {tag} successfully ({self.framerate}fps)")
        size = (width, get_relative_height(im, width)) # makes a height value that maintains aspect ratio to fit in widget

        global frames_complete
        frames_complete = False
        self.all_frames = process_frames(im,size, tag)
        self.frames_chunk = cycle(self.all_frames)

        if frames_complete:
                with contextlib.suppress(Exception):
                    self.next_frame(tag)
        
    def next_frame(self, tag):
        while True:
            with contextlib.suppress(Exception):
                self.loaded_image = (
                    top_queue.get_nowait()
                    if tag == "top_embed"
                    else bottom_queue.get_nowait()
                )
            self.configure(image=next(self.frames_chunk))
            self.bind("<Button-1>", lambda x: self.copy_current(self.url))
            time.sleep(1/self.framerate)
            if self.loaded_image != self.url:
                print(f"<IMAGE_HANDLER> Image changed: {tag}")
                self.load(self.loaded_image, self.tag, self.width, self.bgcolor)

def process_frames(im, size, tag):  # resize and arrange gifs
    frames_chunk = []
    mode = analyseImage(im)["mode"]
    last_frame = im.convert("RGBA")

    for i, frame in enumerate(ImageSequence.Iterator(im)):
        frame_image = Image.new("RGBA", frame.size)
        if mode == "partial":
            frame_image.paste(last_frame)

        frame_image.paste(frame, (0, 0), frame.convert("RGBA"))
        frame_image.thumbnail(size, Image.BILINEAR)
        new_frame = ImageTk.PhotoImage(frame_image)
        frames_chunk.append(new_frame)
        print(f"<IMAGE_HANDLER> Appended frame {i}/{im.n_frames} to frames_chunk")
    print(f"<IMAGE_HANDLER> ({tag}) Encode completed")
    im.close()
    global frames_complete
    frames_complete = True
    return frames_chunk

def get_relative_height(source, mywidth):
    _, height = source.size
    wpercent = (mywidth/float(height))
    return int((float(height)*float(wpercent)))

def analyseImage(im):
    """
    Pre-process pass over the image to determine the mode (full or additive).
    Necessary as assessing single frames isn't reliable. Need to know the mode
    before processing all frames.ll
    """
    results = {
        "size": im.size,
        "mode": "full",
    }

    with contextlib.suppress(EOFError):
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results["mode"] = "partial"
                    break
            im.seek(im.tell() + 1)
    return results
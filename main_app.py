"""
    GNU License

    Copyright © 2023 OneBigLotus


    Thank You For Using YHAM! If you're reading this, you're probably trying to make some modifications to the source code 
    For your own use. I wouldn't recommend it since this was a learning experience, and because this the program is a mess.
    This app is GNU Licenced, and you are free to redistribute or make modifications to the source!
    
    Thanks,
    
    -- OneBigLotus
"""
import os
import sys
from PIL import Image
process_id = os.getpid()
# threading
from threading import Thread
from time import sleep
# custom tkinter for main frontend
import customtkinter
# grab backend
import backend
import tkinter
from tkinter import Text, Menu
from tkinter.scrolledtext import ScrolledText
from tkVideoPlayer import TkinterVideo   
import image_handler as imageHandler
import darkdetect
import webbrowser
from logger_widget import PrintLogger
# get limit of config tables
global session, threadpool, advertisement
# load the session data from last app close from the resources folder

session = backend.load_session_with_fallback()
saved_theme = session.get("theme")
threadpool = []
advertisement = None
try:
    DIRPATH = os.path.dirname(sys.executable)
    theme = (f"{DIRPATH}/userdat/themes/{saved_theme}.json")
    customtkinter.set_default_color_theme(theme)
except FileNotFoundError:
    backend.notify("Theme not found: ")
    customtkinter.set_default_color_theme(backend.load_resource("customtkinter/assets/themes/dark-blue.json"))
    session["theme"] = "dark-blue"

# Console Widget Class
class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        try:  
            self.geometry("600x400")
            self.resizable(False, False)
            self.title("Console")
            self.log_widget = ScrolledText(self,bg='#4a4d54', foreground='#fbfcff', height=self.winfo_height(), width=self.winfo_width(), font=("consolas", "9", "normal"))
            self.log_widget.pack()
            logger = PrintLogger(self.log_widget)
            sys.stdout = logger
            sys.stderr = logger
            self.protocol('WM_DELETE_WINDOW', self.withdraw)  # root is your root window  
        except Exception:
            backend.notify(Exception)
        self.withdraw()

# Tutorial Widget Class
class TutorialVideo(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("1280x720")
        self.title("Tutorial")
        self.resizable(False, False)
        def update_duration(event):
                """ updates the duration after finding the duration """
                duration = vid_player.video_info()["duration"]
                progress_slider["to"] = duration
        
        def update_scale(event):
                """ updates the scale value """
                progress_value.set(vid_player.current_duration())

        def seek(value):
                """ used to seek a specific timeframe """
                vid_player.seek(int(value))


        def skip(value: int):
                """ skip seconds """
                vid_player.seek(int(progress_slider.get())+value)
                progress_value.set(progress_slider.get() + value)


        def play_pause():
                """ pauses and plays """
                if vid_player.is_paused():
                    vid_player.play()
                    play_pause_btn.configure(text="Pause") 

                else:
                    vid_player.pause()
                    play_pause_btn.configure(text="Play")


        def video_ended(event):
                """ handle video ended """
                progress_slider.set(progress_slider["to"])
                play_pause_btn["text"] = "Play"
                progress_slider.set(0)

        def on_closing():
                vid_player.pause()
                play_pause_btn.configure(text="Play")
                self.withdraw()

        vid_player = TkinterVideo(scaled=True, keep_aspect=True, master=self, bg='#4a4d54')
        vid_player.pack(expand=True, fill="both")

        play_pause_btn = customtkinter.CTkButton(self, text=("Play" if vid_player.is_paused() else "Pause"), command=play_pause)
        play_pause_btn.pack()

        skip_plus_5sec = customtkinter.CTkButton(self, text="Skip -5 sec", command=lambda: skip(-5))
        skip_plus_5sec.pack(side="left")

        progress_value = customtkinter.IntVar(self)

        progress_slider = tkinter.Scale(self, variable=progress_value, from_=0, to=0, orient="horizontal", command=seek, bg='#4a4d54', foreground='#fbfcff', borderwidth=0) 
        progress_slider.pack(side="left", fill="x" ,expand=True)

        vid_player.bind("<<Duration>>", update_duration)
        vid_player.bind("<<SecondChanged>>", update_scale)
        vid_player.bind("<<Ended>>", video_ended)

        skip_plus_5sec = customtkinter.CTkButton(self, text="Skip +5 sec", command=lambda: skip(5))
        skip_plus_5sec.pack(side="left")

        vid_player.load(backend.load_resource("resources/Tutorial.mp4"))

        self.protocol('WM_DELETE_WINDOW', on_closing)  # root is your root window
        self.withdraw()

# Application Class
class App(customtkinter.CTk):
    # app variables
    WIDTH = 1225
    HEIGHT = 850 
    def __init__(self):
        super().__init__()
        self.title(f'{backend.program_name}{backend.version_discriminator}')
        self.iconbitmap(backend.load_resource("resources\icon.ico"))
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.minsize(App.WIDTH, App.HEIGHT)
        # call .on_closing() when app gets closed
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # create variables for threaded task
        # checkbox variable for threaded task
        global switch_var, check_var, slider_var, affil_var
        # slider variable for repeating threaded task
        slider_var = customtkinter.IntVar()
        slider_var.trace_add("write", self.update_checkbox)
        switch_var = customtkinter.IntVar()
        check_var = customtkinter.IntVar()
        affil_var = customtkinter.IntVar()
        # images for buttons (placed here because of order of execution)
        GENERATE_IMG = customtkinter.CTkImage(
            light_image=Image.open(backend.load_resource("resources/Generate.png")),
            dark_image=Image.open(backend.load_resource("resources/Generate.png"))
        )
        COPY_IMG = customtkinter.CTkImage(
            light_image=Image.open(backend.load_resource("resources/Copy.png")),
            dark_image=Image.open(backend.load_resource("resources/Copy.png"))
        )
        # Get all the loaded themes
        themes = self.identify_themes()

        # add menubar to enable console
        # get the background of frame
        menubar = Menu(self,bg='black',
                             fg='white',
                             activeforeground='black',
                             activebackground='white')
        self.config(menu=menubar)
        self.option_add('*tearOff', False)
        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Show Console", command= lambda : self.toggle_toplevel(self.console_widget))
        fileMenu.add_command(label="Tutorial", command= lambda : self.toggle_toplevel(self.tutorial_video))
        fileMenu.add_command(label="Join YiffHub Discord", command=lambda : webbrowser.open_new("https://discord.gg/yiffhub"))
        uiScaleMenu = Menu(menubar, name="uiScaleMenu")
        global current_ui_scale
        current_ui_scale = session["ui_scale"]
        # Create the options and add them to the menu
        # Create checkbuttons for different UI scales
        uiScaleMenu.add_command(label="100%", command=lambda: self.change_scale("100%"))
        uiScaleMenu.add_command(label="85%", command=lambda: self.change_scale("85%"))
        uiScaleMenu.add_command(label="70%", command=lambda: self.change_scale("70%"))
        uiScaleMenu.add_command(label="55%", command=lambda: self.change_scale("55%"))

        menubar.add_cascade(label="File", menu=fileMenu)
        menubar.add_cascade(label="UI Scale", menu=uiScaleMenu)
        
        menubar.add_cascade(label="Designed by @OneBigLotus")
        # create a starting topLevel widget
        self.console_widget = ToplevelWindow(self)
        # create a starting tutorial video
        self.tutorial_video = TutorialVideo(self)
        # begin processing repeating thread
        global thread_advertise
        thread_advertise = Thread(daemon=True, target=self.repeat_advertise).start()

        # configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # Left Frame
        self.frame_left = customtkinter.CTkFrame(
            master=self, width=180, corner_radius=0
        )
        self.frame_left.grid(row=0, column=0, sticky="nswe")
        # Left Subframe
        self.iframe1_left = customtkinter.CTkFrame(
            master=self.frame_left, width=self.frame_left.winfo_width(), corner_radius=15  # type: ignore
        )
        self.iframe1_left.grid(row=6, column=0, sticky="nswe")
        # Labels
        self.subframe_title = customtkinter.CTkLabel(
            master=self.iframe1_left,
            width=120,
            height=25,
            text="Disabled",
            text_color="red",
            corner_radius=15,
            font=("Roboto", 15),
        )
        self.subframe_title.grid(
            row=0, column=1, sticky="nswe", padx=20, pady=20)
        self.ad_label = customtkinter.CTkLabel(
            master=self.iframe1_left,
            width=120,
            height=25,
            text="Search Description By Index:",
            font=("Roboto", 10),
            corner_radius=15
        )
        self.ad_label.place(relx = 0.43, rely = 0.18, anchor = "center")
        self.aff_label = customtkinter.CTkLabel(
                master=self.iframe1_left,
                width=120,
                height=25,
                text="Search Affiliate Link By Index:",
                font=("Roboto", 10),
                corner_radius=15
        )
        self.aff_label.place(relx = 0.43, rely = 0.34, anchor = "center")
        self.inv_label = customtkinter.CTkLabel(
                master=self.iframe1_left,
                width=120,
                height=25,
                text="Search Discord Invites By Index:",
                font=("Roboto", 10),
                corner_radius=15
        )
        self.inv_label.place(relx = 0.43, rely = 0.50, anchor = "center")
        self.img1_label = customtkinter.CTkLabel(
                master=self.iframe1_left,
                width=120,
                height=25,
                text="Search Top Images By Index:",
                font=("Roboto", 10),
                corner_radius=15
        )
        self.img1_label.place(relx = 0.43, rely = 0.68, anchor = "center")
        # Subframe Input Entries
        self.img2_label = customtkinter.CTkLabel(
                master=self.iframe1_left,
                width=120,
                height=25,
                text="Search Bottom Images By Index:",
                font=("Roboto", 10),
                corner_radius=15
        )
        self.img2_label.place(relx = 0.43, rely = 0.84, anchor = "center")
        # Current Advertisement
        self.entry_advertisement = customtkinter.CTkEntry(
            master=self.iframe1_left,
            state="disabled",
            width=120,
            height=25,
            border_width=2,
            corner_radius=15,
        )
        self.entry_advertisement.grid(
            row=1, column=1, sticky="nswe", padx=20, pady=20)

        # Index for Affiliate Link
        self.entry_affiliate = customtkinter.CTkEntry(
            master=self.iframe1_left,
            state="disabled",
            width=120,
            height=25,
            border_width=2,
            corner_radius=15,
        )
        self.entry_affiliate.grid(
            row=2, column=1, sticky="nswe", padx=20, pady=20)
        # Index for invite
        self.entry_invite = customtkinter.CTkEntry(
            master=self.iframe1_left,
            state="disabled",
            width=120,
            height=25,
            border_width=2,
            corner_radius=15,
        )
        self.entry_invite.grid(
            row=3, column=1, sticky="nswe", padx=20, pady=20)
        # Index for Top Image
        self.entry_image1 = customtkinter.CTkEntry(
            master=self.iframe1_left,
            state="disabled",
            width=120,
            height=25,
            border_width=2,
            corner_radius=15,
        )
        self.entry_image1.grid(
            row=4, column=1, sticky="nswe", padx=20, pady=20)
        # Index for Bottom Image
        self.entry_image2 = customtkinter.CTkEntry(
            master=self.iframe1_left,
            state="disabled",
            width=120,
            height=25,
            border_width=2,
            corner_radius=15,
        )
        self.entry_image2.grid(
            row=5, column=1, sticky="nswe", padx=20, pady=20)
        # Middle Frame
        self.frame_middle = customtkinter.CTkFrame(
            master=self, corner_radius=15
        )
        self.frame_middle.grid_rowconfigure(0, weight=1)
        self.frame_middle.grid_columnconfigure(0, weight=1)
        self.frame_middle.grid(
            row=0, column=1, sticky="nswe", padx=20, pady=20)
        # Right Frame
        self.frame_right = customtkinter.CTkFrame(
            master=self, corner_radius=15)
        self.frame_right.grid(row=0, column=2, sticky="nswe", padx=20, pady=20)
        # configure grid layout (3x7)
        self.frame_right.rowconfigure((0, 1, 2, 3), weight=1)
        self.frame_right.rowconfigure(7, weight=10)
        self.frame_right.columnconfigure((0, 1), weight=1)
        self.frame_right.columnconfigure(2, weight=0)
        # Objects Left Frame
        self.seed_display = customtkinter.CTkEntry(
            master=self.frame_left,
            placeholder_text="",
            state="disabled",
            width=215,
            height=25,
            border_width=2,
            corner_radius=15
        )
        self.seed_display.grid(row=7, column=0, pady=10, padx=20)
        self.button1 = customtkinter.CTkButton(
            master=self.frame_left,
            text="Create Advertisement",
            image=GENERATE_IMG,
            command=self.advertise
        )
        self.button1.grid(row=8, column=0, pady=10, padx=20)

        self.button2 = customtkinter.CTkButton(
            master=self.frame_left,
            text="Copy To Clipboard",
            image=COPY_IMG,
            command=self.copy_advertisement
        )
        self.button2.grid(row=9, column=0, pady=10, padx=20)

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(
            row=10, column=0, padx=20, pady=(10, 10))
        self.theme_optionmenu = customtkinter.CTkOptionMenu(self.frame_left, values=themes,
                                                            command=self.change_color_mode_event)
        self.theme_optionmenu.grid(
            row=11, column=0, padx=20, pady=(10, 3))    

        self.m_check1 = customtkinter.CTkCheckBox(
            master=self.frame_left,
            state="normal",
            text="Keep Text",
            command=lambda: self.checkbox_event(
                self.m_check1, "text_lock"
            )
        )
        self.m_check1.grid(row=12, column=0, padx=0, pady=4)

        self.m_check2 = customtkinter.CTkCheckBox(
            master=self.frame_left,
            state="normal",
            text="Keep Affiliate Link",
            command=lambda: self.checkbox_event(
                self.m_check2, "preset_switch"
            )
        )
        self.m_check2.grid(row=13, column=0, padx=0, pady=4)

        self.m_check3 = customtkinter.CTkCheckBox(
            master=self.frame_left,
            state="normal",
            text="Keep Invite",
            command=lambda: self.checkbox_event(
                self.m_check3, "invite_lock"
             )
        )
        self.m_check3.grid(row=14, column=0, padx=0, pady=4)

        self.m_check4 = customtkinter.CTkCheckBox(
            master=self.frame_left,
            state="normal",
            text="Keep Top Image",
            command=lambda: self.checkbox_event(
                self.m_check4, "top_image_lock"
            )
        )
        self.m_check4.grid(row=15, column=0, padx=0, pady=4)

        self.m_check5 = customtkinter.CTkCheckBox(
            master=self.frame_left,
            state="normal",
            text="Keep Bottom Image",
            command=lambda: self.checkbox_event(
                self.m_check5, "bottom_image_lock"
            )

        )
        self.m_check5.grid(row=16, column=0, padx=0, pady=4)

        self.switch_1 = customtkinter.CTkSwitch(
            master=self.frame_left,
            variable=switch_var,
            command=lambda: self.toggle_manual_widget(
                self.iframe1_left, self.subframe_title
            ),
            text="Random",
        )

        self.switch_1.grid(
            row=5, column=0, columnspan=10, sticky="nswe", pady=20, padx=20
        )
    # Objects Middle Frame
        # text preview (No customtkinter .delete attribute, using tkinter default library textbox)
        self.text_preview = Text(
            master=self.frame_middle,
            font=("Robotto", 13),
            borderwidth=0,
            foreground=self.get_system_appearance("Text"),
            bg=self.get_system_appearance("Widget",self.frame_middle),
            state="disabled"
        )
        self.text_preview.grid(row=0, column=0, sticky="nswe")
        # text explanation
        self.text_explanation = customtkinter.CTkLabel(
            master=self.frame_middle,
            text="Left Click: Load Preset",
            font=("Robotto", 12)
        )
        self.text_explanation.grid(row=1, column=0, sticky="w", padx=5)
        # Checkbox to overwrite presets with
        self.overwrite_button = customtkinter.CTkCheckBox(
            master=self.frame_middle, text="Overwrite Preset:", command=lambda: print(f"overwrite preset: {self.overwrite_button.get()}")
        )
        self.overwrite_button.grid(row=1, column=0,sticky="w", padx=140, pady=4)
        # Switch to control affiliate links / bottom images
        self.preset_switch = customtkinter.CTkSwitch(
            master=self.frame_middle, variable=affil_var, onvalue=1, offvalue=0, text="", command=self.toggle_preset_switch
        )
        self.preset_switch.grid(row=1, column=0,sticky="n", padx=250, pady=4)
        # save states for favorite ads
        self.preset_1 = customtkinter.CTkButton(
            master=self.frame_middle,
            text="",
            textvariable="preset_1",
            command=lambda: self.preset_menu("preset_1", session.get("preset_1")),
            corner_radius=15
        )
        self.preset_1.grid(
            row=2, column=0, sticky="nsw", pady=4, padx=1
        )
        self.preset_2 = customtkinter.CTkButton(
            master=self.frame_middle,
            text="",
            textvariable="preset_2",
            command=lambda: self.preset_menu("preset_2", session.get("preset_2")),
            corner_radius=15
        )
        self.preset_2.grid(
            row=3, column=0, sticky="nsw", pady=4, padx=1
        )
        self.preset_3 = customtkinter.CTkButton(
            master=self.frame_middle,
            text="",
            textvariable="preset_3",
            command=lambda: self.preset_menu("preset_3", session.get("preset_3")),
            corner_radius=15
        )
        self.preset_3.grid(
            row=4, column=0, sticky="nsw", pady=4, padx=1
        )
        self.preset_4 = customtkinter.CTkButton(
            master=self.frame_middle,
            text="",
            textvariable="preset_4",
            command=lambda: self.preset_menu("preset_4", session.get("preset_4")),
            corner_radius=15
        )
        self.preset_4.grid(
            row=5, column=0, sticky="nsw", pady=4, padx=1
        )
        self.preset_5 = customtkinter.CTkButton(
            master=self.frame_middle,
            text="",
            textvariable="preset_5",
            command=lambda: self.preset_menu("preset_5", session.get("preset_5")),
            corner_radius=15
        )
        self.preset_5.grid(
            row=2, column=0, sticky="ns", pady=4, padx=250
        )
        self.preset_6 = customtkinter.CTkButton(
            master=self.frame_middle,
            text="",
            textvariable="preset_6",
            command=lambda: self.preset_menu("preset_6", session.get("preset_6")),
            corner_radius=15
        )
        self.preset_6.grid(
            row=3, column=0, sticky="ns", pady=4, padx=250
        )
        self.preset_7 = customtkinter.CTkButton(
            master=self.frame_middle,
            text="",
            textvariable="preset_7",
            command=lambda: self.preset_menu("preset_7", session.get("preset_7")),
            corner_radius=15
        )
        self.preset_7.grid(
            row=4, column=0, sticky="ns", pady=4, padx=250
        )
        self.preset_8 = customtkinter.CTkButton(
            master=self.frame_middle,
            text="",
            textvariable="preset_8",
            command=lambda: self.preset_menu("preset_8", session.get("preset_8")),
            corner_radius=15
        )
        self.preset_8.grid(
            row=5, column=0, sticky="ns", pady=4, padx=250
        )
        self.preset_9 = customtkinter.CTkButton(
            master=self.frame_middle,
            text="",
            textvariable="preset_9",
            command=lambda: self.preset_menu("preset_9", session.get("preset_9")),
            corner_radius=15
        )
        self.preset_9.grid(
            row=2, column=0, sticky="nse", pady=4, padx=10
        )
        self.preset_10 = customtkinter.CTkButton(
            master=self.frame_middle,
            text="",
            textvariable="preset_10",
            command=lambda: self.preset_menu("preset_10", session.get("preset_10")),
            corner_radius=15
        )
        self.preset_10.grid(
            row=3, column=0, sticky="nse", pady=4, padx=10
        )
        self.preset_11 = customtkinter.CTkButton(
            master=self.frame_middle,
            text="",
            textvariable="preset_11",
            command=lambda: self.preset_menu("preset_11", session.get("preset_11")),
            corner_radius=15
        )
        self.preset_11.grid(
            row=4, column=0, sticky="nse", pady=4, padx=10
        )
        self.preset_12 = customtkinter.CTkButton(
            master=self.frame_middle,
            text="",
            textvariable="preset_12",
            command=lambda: self.preset_menu("preset_12", session.get("preset_12")),
            corner_radius=15
        )
        self.preset_12.grid(
            row=5, column=0, sticky="nse", pady=4, padx=10
        )
        self.widgets = [
            self.preset_1,
            self.preset_2,
            self.preset_3,
            self.preset_4,
            self.preset_5,
            self.preset_6,
            self.preset_7,
            self.preset_8,
            self.preset_9,
            self.preset_10,
            self.preset_11,
            self.preset_12,
        ]
        # Objects Right Frame
        # Lables for image embeds
        self.img1_label_Bold = customtkinter.CTkLabel(
                master=self.frame_right,
                width=120,
                height=25,
                text="Top Image:\n(left click to copy image link)",
                font=("Roboto", 15),
                corner_radius=15
        )
        self.img1_label_Bold.place(relx = 0.5, rely = 0.1, anchor = "center")
        self.img2_label_Bold = customtkinter.CTkLabel(
                master=self.frame_right,
                width=120,
                height=25,
                text="Bottom Image:\n(left click to copy image link)",
                font=("Roboto", 15),
                corner_radius=15
        )
        self.img2_label_Bold.place(relx = 0.5, rely = 0.48, anchor = "center")
        # Embed Labels
        # Top Label
        self.topLabel = imageHandler.ImageLabel(
            self.frame_right)
        self.topLabel.place(relx=0.5, rely=0.3, anchor="center")
        self.topLabel.configure(bg=None)
        # Bottom Label
        self.bottomLabel = imageHandler.ImageLabel(
            self.frame_right)
        self.bottomLabel.place(relx=0.5, rely=0.7, anchor="center")
        self.bottomLabel.configure(bg=None)
        self.slider_1 = customtkinter.CTkSlider(
            master=self.frame_right,
            from_=5,
            to=10,
            number_of_steps=5,
            variable=slider_var,
        )
        self.slider_1.grid(
            row=8, column=1, columnspan=15, pady=10, padx=20, sticky="we"
        )
        self.check_1 = customtkinter.CTkCheckBox(
            master=self.frame_right, variable=check_var, text="Copy Interval: ", command=self.toggle_slider
        )
        self.check_1.grid(row=9, column=0, columnspan=10,
                          pady=10, padx=15, sticky="w")
        self.check_2 =  customtkinter.CTkCheckBox(
            master=self.frame_right, text="Hide Links:", command=self.toggle_link_hide
        )
        self.check_2.grid(row=10, column=0, columnspan=10,
                          pady=10, padx=15, sticky="w")
# Initialize values at runtime
        sources = backend.send_source()
        global ads, affiliates, invites, img1, img2, placeholder_text, advertisement
        ads = sources["Advertisements"]
        affiliates = sources["Affiliates"]
        invites = sources["Invites"]
        img1 = sources["TopImage"]
        img2 = sources["BottomImage"]
        # bind entry placeholder text behavior
        placeholder_text = "Between 1-"
        for entry in ((self.entry_advertisement, ads), (self.entry_affiliate, affiliates), (self.entry_invite, invites), (self.entry_image1, img1), (self.entry_image2, img2)):
            entry[0].bind('<Button-1>', lambda _,
                          p=entry[0]: self.on_focus_in(p))
            entry[0].bind('<FocusOut>', lambda _, p=entry[0], q=entry[1]: self.on_focus_out(p, (f"{placeholder_text}{len(q)}")))
        # set up slider and mode toggle loadstates
        self.populate_entries()
        cached_advertisement = session.get("last_advertisement")
        last_advertisement = self.verify_seed(cached_advertisement)
        self.update_seed(last_advertisement)
        # initialize the app preview
        self.update_preview(
            (last_advertisement[0] + "\n\nAffiliate Link: " + last_advertisement[1] + "\n\nDiscord Invite: "+last_advertisement[2]))
        # This updates the global variable. This is not redundancy, though this code overall is shit.
        advertisement = last_advertisement
        # set slider value
        self.slider_1.set(session["rate"])
        self.slider_1.configure(state="disabled")
        # load the app mode
        self.change_scaling_event(session.get("ui_scale"))
        if session["random_enabled"] == 1:
            self.switch_1.toggle()
        if session["rate_enabled"] == 1:
            self.check_1.toggle()
        # get component locks
        if session["text_lock"] == 1:
            self.m_check1.toggle()
        if session["affiliate_lock"] == 1:
            self.m_check2.toggle()
        if session["invite_lock"] == 1:
            self.m_check3.toggle()
        if session["top_image_lock"] == 1:
            self.m_check4.toggle()
        if session["bottom_image_lock"] == 1:
            self.m_check5.toggle()
        if session["preset_switch"] == 1:
            self.preset_switch.select()
            self.toggle_preset_switch()
        else:
            self.preset_switch.configure(text="Two Images")
        if session["hide_links"] == True:
            self.check_2.select()
        # set appearance from session 
        self.appearance_mode_optionemenu.set(session.get("appearance"))
        self.change_appearance_mode_event(session.get("appearance"))
        # set theme optionmenu
        self.theme_optionmenu.set(session.get("theme"))
        # set all preset entries
        self.update_presets()
        # update embeds
        self.loadEmbeds(last_advertisement)
        # bind updating the window to configuring color
        self.bind("<Configure>", lambda _ : self.match_appearance())
        

# Functions
    # scale UI for smaller devices
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)
        
    def toggle_link_hide(self):
        session["hide_links"] = not session["hide_links"]
        print(f'<MAIN> Hide links: {session["hide_links"]}')

    def change_scale(self, value):
        print("<MAIN> UI scale changed to:", value)
        session["ui_scale"] = value
        self.change_scaling_event(value)
    
    #set up colors to theme text objects that do not sync with custom tkinter   
    def get_system_appearance(self, type, widget_parent=None):
        # set text colors
        text_colors = {
                    "Light" : 'black',
                    "Dark" : 'gray90',
                    "System" : 'black' if darkdetect.isLight() else 'gray90'
                } 
        if widget_parent != None:
            colors = widget_parent.cget("fg_color")
            widget_colors = {
                "Light" : colors[0],
                "Dark" : colors[1],
                "System" : colors[0] if darkdetect.isLight() else colors[1]
            }
        return text_colors.get(self.appearance_mode_optionemenu.get()) if type == "Text" else widget_colors.get(self.appearance_mode_optionemenu.get())
    
    # get all themes
    def identify_themes(self):
        # sourcery skip: merge-list-append, move-assign-in-block
        themes = []
        try:
            themes_folder = f"{DIRPATH}/userdat/themes"
            for theme in os.listdir(themes_folder):
                if theme.endswith('.json'):
                    theme = str(theme.split(".")[0])
                    themes.append(theme)
        except Exception:
            print("<Main> No theme directory found")
        return themes

    # app appearence mode button
    def change_appearance_mode_event(self, new_appearance_mode: str):
        app_appearance = self.appearance_mode_optionemenu.get()
        customtkinter.set_appearance_mode(new_appearance_mode)
        # update the text and label backgrounds
        # text
        if self.subframe_title.cget("text") != "Disabled":
            self.subframe_title.configure(text_color=self.get_system_appearance("Text"))
        else:
            self.subframe_title.configure(text_color="red")
        self.match_appearance()
        global session
        session["appearance"] = app_appearance

    def change_color_mode_event(self, new_color_mode: str):
        global session
        session["theme"] = new_color_mode
        print("<MAIN> App Restarting To Apply Changes")
        self.restart()

    def verify_seed(self, cached_advertisement):
        last_advertisement = None
        
        config_data_list = [ads, affiliates, invites, img1, img2]
        try:
            for entry in cached_advertisement:
                list_index = cached_advertisement.index(entry)
                if cached_advertisement[list_index] in config_data_list[list_index]:
                    continue
                else:
                    raise ValueError("Entry not found in config_data_list")
            
            last_advertisement = cached_advertisement
        except ValueError:
            print("<MAIN> Session data not found in config")
            last_advertisement = [ads[0], affiliates[0], invites[0], img1[0], img2[0]]
            # if the loop finished and the last session data is intact then load it, otherwise load defaults
        
        self.update_seed(last_advertisement)
        return last_advertisement
            
    def populate_entries(self):
        # update the values in all of the entries
        for entry in ((self.entry_advertisement, ads), (self.entry_affiliate, affiliates), (self.entry_invite, invites), (self.entry_image1, img1), (self.entry_image2, img2)):
            x = None
            if entry[0].cget("state") == "disabled":
                x = True
                entry[0].configure(state="normal")
            entry[0].delete(0, 'end')
            entry[0].insert(0, (f"{placeholder_text}{len(entry[1])}"))
            if x is True:
                entry[0].configure(state="disabled")
        print("<MAIN> Manual entry placeholders populated")

    def update_seed(self, this_advertisement):
        # update the seed display
        seed=[ads.index(this_advertisement[0])+1, affiliates.index(this_advertisement[1])+1, invites.index(this_advertisement[2])+1,img1.index(this_advertisement[3])+1, img2.index(this_advertisement[4])+1]
        self.seed_display.configure(state="normal")
        self.seed_display.delete(0, 'end')
        self.seed_display.insert(0, f"Currently Loaded: {seed}")
        self.seed_display.configure(state="disabled")
        print("<MAIN> Seed entry populated")
        
    # entry text behavior functions
    def on_focus_in(self, entry):
        if entry.cget("state") == "normal":
            entry.delete(0, 'end')
    def on_focus_out(self, entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)

    # preset switch behavior
    def toggle_preset_switch(self):
        
        if not affil_var.get():
            self.preset_switch.configure(text="Two Images")
            session["preset_switch"] = 0
        else:
            self.preset_switch.configure(text="Affiliate Link")
            session["preset_switch"] = 1
        
    # toggle all items in a frame
    def toggle_manual_widget(self, entry, label):
        def configure_widgets(text, state):
            self.switch_1.configure(text=text)
            self.check_1.configure(state=state)
            self.m_check1.configure(state=state)
            self.m_check2.configure(state=state)
            self.m_check3.configure(state=state)
            self.m_check4.configure(state=state)
            self.m_check5.configure(state=state)
        # grid_slaves without arguments returns a list
        widget = entry.grid_slaves()  
        for element in widget:
            if isinstance(element, customtkinter.CTkEntry):
                if element.cget("state") == "disabled":
                    element.configure(state="normal")
                    label.configure(text="Manual Input:",
                                    text_color=self.get_system_appearance("Text"))
                    configure_widgets("Manual", "disabled")
                    # set the thread event to stop looping if it's happening
                else:
                    element.configure(state="disabled")
                    label.configure(text="Disabled", text_color="red")
                    configure_widgets("Random", "normal")
        self.populate_entries()
        session["random_enabled"] = self.switch_1.get()

    # handle checkbox
    def update_checkbox(
        self, *_
    ):  # args is not used here, but saved in case I want to make it adjust other variables.
        self.check_1.configure(
            text=(f"Copy Interval: {str(slider_var.get())} sec")
        )
        session["rate"] = self.slider_1.get()

    # save states for all checkboxes
    def checkbox_event(self, name, data):
        session[data] = name.get()
        print(data, name.get())
    
    # handles the popup that confirms the name of the preset.
    def preset_menu(self, save_name, preset):
        # read the state of the Overwrite checkbox. if the checkbox is not toggled, simply load
        if not self.overwrite_button.get():
            preset_data = preset[1]
            self.load_preset(preset_data)     
        else:
            self.overwrite_button.deselect()
            entry_dialogue = customtkinter.CTkToplevel(self)
            entry_dialogue.title("Entry Dialogue")
            entry_dialogue.geometry("200x100")

            name_label = customtkinter.CTkLabel(
                entry_dialogue, text="Create a Name For Preset:", font=("Robotto", 10))
            name_label.pack()

            name_entry = customtkinter.CTkEntry(entry_dialogue)
            name_entry.pack(fill=customtkinter.X)

            def save_preset():
                if len(name_entry.get()) < 15 and len(name_entry.get()) > 0:
                    # Set With A Tuple Of The Current Advertisement To Snapshot
                    session[save_name] = (name_entry.get(), advertisement)
                    self.restart()
                else:  
                    backend.notify("Name must be less than 15 characters and cannot be blank")
                entry_dialogue.destroy()

            submit_button = customtkinter.CTkButton(
                entry_dialogue, text="Submit", command=lambda: save_preset())
            submit_button.pack()

            tooltip = customtkinter.CTkLabel(
                entry_dialogue, text="Esc = Cancel", font=("Helvetica bold", 10))
            tooltip.pack()

            entry_dialogue.overrideredirect(True)
            entry_dialogue.bind("<Escape>", lambda _: entry_dialogue.destroy())
            
            x = self.winfo_x()
            y = self.winfo_y()
            w = entry_dialogue.winfo_width()
            h = entry_dialogue.winfo_height()  
            entry_dialogue.geometry("%dx%d+%d+%d" % (w, h, x + 500, y + 350))
            entry_dialogue.grab_set()
            entry_dialogue.focus_force()
            entry_dialogue.mainloop()

    def load_preset(self, preset):  # sourcery skip: extract-method
        # attempt find the numeric indexes of the saved advertisement, or clear the preset if the data is no longer saved.
        try: 
            preset_data = self.verify_seed(preset)
            text=ads.index(preset_data[0])+1
            affiliate = affiliates.index(preset_data[1])+1
            invite_link = invites.index(preset_data[2])+1
            top_image = img1.index(preset_data[3])+1
            bottom_image = img2.index(preset_data[4])+1
            global advertisement
            advertisement = backend.create_ad(1,0,0,0,0,0,session.get("last_advertisement"),text,affiliate,invite_link,top_image,bottom_image)
            self.update_preview(advertisement[0] + "\n\nAffiliate Link: " + advertisement[1] + "\n\nDiscord Invite: "+advertisement[2])
            session["last_advertisement"] = advertisement
            # update embed global variables for new images
            self.update_seed(advertisement)
            self.loadEmbeds(advertisement)
        except ValueError:
            backend.notify(f"Preset {preset} could not be loaded.")    
        except Exception as e:
            backend.notify()

           
    # update the preset buttons
    def update_presets(self):
        for x in self.widgets:
            x.configure(text=str((session[x.cget("textvariable")])[0]))

      # update the textbox in the center of the application
    def update_preview(self, ad):
        # update the text preview
        self.text_preview.configure(state="normal")
        self.text_preview.delete('1.0', "end")
        self.text_preview.insert("0.0", ad)
        self.text_preview.configure(state="disabled")
    
    # TODO Rename this here and in `change_appearance_mode_event` and `fix_appearance`
    def match_appearance(self):
        self.topLabel.configure(
            background=self.get_system_appearance("Widget", self.topLabel.master)
        )
        self.bottomLabel.configure(
            background=self.get_system_appearance(
                "Widget", self.bottomLabel.master
            )
        )
        self.text_preview.configure(
            background=self.get_system_appearance("Widget", self.frame_left),
            fg=self.get_system_appearance("Text"),
        )
    
    # request an advertisement from backend

    def advertise(self):  # sourcery skip: extract-method  # sourcery skip: extract-method
        entries = [self.entry_advertisement.get(),self.entry_affiliate.get() ,self.entry_invite.get(),self.entry_image1.get(),self.entry_image2.get()]
        invalid_input_found = False
        for i in entries:
            try:
                int(i)
            except ValueError:
                invalid_input_found = True
                break  # Exit loop as soon as invalid input is found  
            
        if self.switch_1.get() and invalid_input_found:    
            backend.notify("Error: Non-numeric or empty input")        
        else: 
            global advertisement
            advertisement = backend.create_ad(
                self.switch_1.get(),  # mode manual/random
                self.m_check1.get(),  # text lock
                self.m_check2.get(),  # affiliate lock
                self.m_check3.get(),  # invite lock
                self.m_check4.get(),  # top image lock
                self.m_check5.get(),  # bottom image lock
                session.get("last_advertisement"),  # cached advertisement
                self.entry_advertisement.get(),  # advertisement text entry
                self.entry_affiliate.get(), # affiliate link entry
                self.entry_invite.get(),  # invite entry
                self.entry_image1.get(),  # top image entry
                self.entry_image2.get()  # bottom image entry
            )
            if self.check_1.get():
                self.copy_advertisement()

            self.update_preview((advertisement[0] + "\n\nAffiliate Link: " + advertisement[1] + "\n\nDiscord Invite: "+advertisement[2]))
            session["last_advertisement"] = advertisement
            # update embed global variables for new images
            self.loadEmbeds(advertisement)
            # update the embed to display current advertisement
            self.update_seed(advertisement)


    def repeat_advertise(self):
        print("<MAIN> Worker thread initialized")
        while True:
            try:
                if check_var.get() and (not self.switch_1.get()):
                    self.advertise()
                    sleep(slider_var.get())
                else:
                    sleep(.5)
            except Exception:
                    print("<MAIN> RepeatLoop failed an itteration")
                    
    def copy_advertisement(self):
       backend.copy(advertisement, affil_var, session.get("hide_links"))

    # reload embeds
    def loadEmbeds(self, advertisement):
        # load data from last advertisement if no current advertisement is provided 
        top_Image, bottom_Image = advertisement[3], advertisement[4]
        # Send the image URLs to the active thread queue
        imageHandler.top_queue.put(top_Image)
        imageHandler.bottom_queue.put(bottom_Image)
        def create_top_thread(label,image,tag):
            label.load(
            image ,tag, self.frame_left.winfo_reqwidth(), self.frame_left.cget("fg_color")
            )
        if len(threadpool) <2:
            thread1= Thread(daemon=True,target=lambda:create_top_thread(self.topLabel, top_Image, "top_embed")).start()
            thread2=Thread(daemon=True,target=lambda:create_top_thread(self.bottomLabel, bottom_Image,"bottom_embed")).start()
            threadpool.append(thread1)
            threadpool.append(thread2)
            
    # handle randomization slider and call threading object 
    def toggle_slider(self):
        if (self.check_1.get() == 1) and (self.switch_1.get() == 0
                                          ):  # checks if Checkbox is enabled and manual is disabled
            session["rate_enabled"] = 1
            self.slider_1.configure(state="normal")
        else:
            session["rate_enabled"] = 0
            self.slider_1.configure(state="disabled")

        # Manages the console        
    def toggle_toplevel(self, widget):
        try:
            if not widget.winfo_viewable(): 
               widget.deiconify()  # Bring Window to front
               if widget == self.tutorial_video:
                   widget.play()
            else:
                widget.focus()  
        except Exception:
            print("<MAIN> Error detecting widget.winfo; regenerating")
            # Create a new Window
            widget = ToplevelWindow(self)

    # closing protocol
    def on_closing(self):
        backend.save_object(session)
        self.destroy()
        # finally, fully shut down the application and all subprocesses 
        os.kill(process_id, 9)

    def restart(self):
        backend.save_object(session)
        self.destroy()
        # restart the subprocess
        os.execl(sys.executable, sys.executable, os.path.relpath(r"main_app.py"))

# def looping main application
# today() to get current date
if __name__ == "__main__":
    #from datetime import datetime
    #date = datetime(2023, 5, 20)
    #now = datetime.now()
    app = App()
    app.mainloop()
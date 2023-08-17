import tkinter as tk
from tkinter import filedialog
from threading import Thread
from WebCamClone import WebCamClone

class WebCamCloneGUI:
    def __init__(self, master):
        self.master = master
        master.title("WebCamClone GUI")

        self.vc = None
        self.thread = None

        self.top_frame = tk.Frame(master)
        self.top_frame.pack(pady=10)

        self.middle_frame = tk.Frame(master)
        self.middle_frame.pack(pady=10)

        self.bottom_frame = tk.Frame(master)
        self.bottom_frame.pack(pady=10)

        self.real_feed_button = tk.Button(self.top_frame, text="Real Feed", command=self.switch_to_webcam, width=15, height=2)
        self.real_feed_button.pack(side=tk.LEFT, padx=5)

        self.virtual_feed_button = tk.Button(self.top_frame, text="Virtual Feed", command=self.switch_to_video, state=tk.DISABLED, width=15, height=2)
        self.virtual_feed_button.pack(side=tk.LEFT, padx=5)

        self.record_button = tk.Button(self.middle_frame, text="Start Recording", command=self.start_recording, state=tk.DISABLED, width=15, height=2)
        self.record_button.pack(side=tk.LEFT, padx=5)

        self.stop_record_button = tk.Button(self.middle_frame, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED, width=15, height=2)
        self.stop_record_button.pack(side=tk.LEFT, padx=5)

        self.selected_file_entry = tk.Label(self.bottom_frame, text="No Video Selected", state=tk.NORMAL)
        self.selected_file_entry.pack(side=tk.TOP, padx=5, pady=5)

        self.select_button = tk.Button(self.bottom_frame, text="Select Video File", command=self.select_file, state=tk.DISABLED)
        self.select_button.pack(side=tk.BOTTOM)

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_vc(self):
        if self.vc is None:
            self.vc = WebCamClone()
            self.thread = Thread(target=self.vc.startWebcamClone)
            self.thread.start()
            self.virtual_feed_button.config(state=tk.NORMAL)
            self.record_button.config(state=tk.NORMAL)
            self.select_button.config(state=tk.NORMAL)

    def switch_to_webcam(self):
        if self.vc is None:
            self.start_vc()
        else:
            self.vc.switch_to_webcam()

    def switch_to_video(self):
        if self.vc is not None:
            self.vc.switch_to_video()

    def start_recording(self):
        if self.vc is not None:
            filename = filedialog.asksaveasfilename(defaultextension=".mp4")
            if filename:
                self.vc.start_recording(filename)
                self.record_button.config(state=tk.DISABLED)
                self.stop_record_button.config(state=tk.NORMAL)

    def stop_recording(self):
        if self.vc is not None:
            self.vc.stop_recording()
            self.record_button.config(state=tk.NORMAL)
            self.stop_record_button.config(state=tk.DISABLED)

    def select_file(self):
        if self.vc is not None:
            filename = filedialog.askopenfilename()
            if filename:
                # self.selected_file_entry.config(state=tk.NORMAL)
                # self.selected_file_entry.delete(0, tk.END)
                # self.selected_file_entry.insert(0, filename)
                # self.selected_file_entry.config(state=tk.DISABLED)
                self.selected_file_entry.config(text=filename)
                self.vc.set_video_path(filename)

    def on_closing(self):
        if self.vc is not None:
            self.vc.close()
            if self.thread is not None:
                self.thread.join()
                self.thread = None
            root.destroy()
        root.destroy()

root = tk.Tk()
my_gui = WebCamCloneGUI(root)
root.mainloop()

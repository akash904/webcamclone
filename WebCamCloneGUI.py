import tkinter as tk
from tkinter import filedialog, messagebox
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

        self.live_feed_button = tk.Button(self.top_frame, text="Live Feed", command=self.switch_to_webcam, width=15, height=2)
        self.live_feed_button.pack(side=tk.LEFT, padx=5)

        self.virtual_feed_button = tk.Button(self.top_frame, text="Virtual Feed", command=self.switch_to_video, state=tk.DISABLED, width=15, height=2)
        self.virtual_feed_button.pack(side=tk.LEFT, padx=5)

        self.record_button = tk.Button(self.middle_frame, text="Start Recording", command=self.start_recording, state=tk.DISABLED, width=15, height=2)
        self.record_button.pack(side=tk.LEFT, padx=5)

        self.stop_record_button = tk.Button(self.middle_frame, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED, width=15, height=2)
        self.stop_record_button.pack(side=tk.LEFT, padx=5)

        self.selected_file_entry = tk.Label(self.bottom_frame, text="No Video File Selected", state=tk.NORMAL)
        self.selected_file_entry.pack(side=tk.TOP, padx=5, pady=5)

        self.status_label = tk.Label(self.bottom_frame, text="Ready", fg="green", font=("Arial", 10, "bold"))
        self.status_label.pack(side=tk.TOP, padx=5, pady=2)

        self.select_button = tk.Button(self.bottom_frame, text="Select Video File", command=self.select_file, state=tk.DISABLED, width=30, height=2)
        self.select_button.pack(side=tk.BOTTOM, padx=5)

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_vc(self):
        if self.vc is None:
            # Show loading feedback
            self.live_feed_button.config(state=tk.DISABLED, text="Starting...")
            self.status_label.config(text="Creating virtual camera...", fg="orange")
            self.master.update()  # Force GUI update
            
            try:
                # Step 1: Create WebCamClone object with callback
                self.status_label.config(text="Initializing camera resources...", fg="orange")
                self.master.update()
                self.vc = WebCamClone(on_feed_started=self.on_feed_started_callback)
                
                # Step 2: Start the thread
                self.status_label.config(text="Starting live feed...", fg="orange")
                self.master.update()
                self.thread = Thread(target=self.vc.startWebcamClone)
                self.thread.start()
                
                # Step 3: Enable buttons (but don't update status yet - wait for callback)
                self.virtual_feed_button.config(state=tk.NORMAL)
                self.record_button.config(state=tk.NORMAL)
                self.select_button.config(state=tk.NORMAL)
                self.live_feed_button.config(state=tk.NORMAL, text="Live Feed")
                
            except Exception as e:
                # Reset button state on error
                self.live_feed_button.config(state=tk.NORMAL, text="Live Feed")
                self.status_label.config(text="Error", fg="red")
                print(f"Error starting virtual camera: {e}")
                # Show error message to user
                tk.messagebox.showerror("Error", f"Failed to start virtual camera: {e}")
    
    def on_feed_started_callback(self):
        """Called when the feed actually starts"""
        self.status_label.config(text="Live Feed Active", fg="green")

    def switch_to_webcam(self):
        if self.vc is None:
            # Show loading status immediately when Live Feed is clicked
            self.status_label.config(text="Live Feed Loading...", fg="orange")
            self.master.update()  # Force GUI update
            self.start_vc()
        else:
            try:
                self.status_label.config(text="Switching to Live Feed...", fg="orange")
                self.master.update()
                self.vc.switch_to_webcam()
                self.status_label.config(text="Live Feed Active", fg="green")
            except Exception as e:
                print(f"Error switching to webcam: {e}")
                self.status_label.config(text="Error", fg="red")
                tk.messagebox.showerror("Error", f"Failed to switch to webcam: {e}")

    def switch_to_video(self):
        if self.vc is not None:
            try:
                self.vc.switch_to_video()
                self.status_label.config(text="Virtual Feed Active", fg="blue")
            except Exception as e:
                print(f"Error switching to video: {e}")
                tk.messagebox.showerror("Error", f"Failed to switch to video: {e}")

    def start_recording(self):
        if self.vc is not None:
            filename = filedialog.asksaveasfilename(defaultextension=".mp4")
            if filename:
                try:
                    self.vc.start_recording(filename)
                    self.record_button.config(state=tk.DISABLED, text="Recording...")
                    self.stop_record_button.config(state=tk.NORMAL)
                    self.status_label.config(text="Recording...", fg="red")
                except Exception as e:
                    print(f"Error starting recording: {e}")
                    tk.messagebox.showerror("Error", f"Failed to start recording: {e}")

    def stop_recording(self):
        if self.vc is not None:
            try:
                self.vc.stop_recording()
                self.record_button.config(state=tk.NORMAL, text="Start Recording")
                self.stop_record_button.config(state=tk.DISABLED)
                self.status_label.config(text="Recording Stopped", fg="orange")
            except Exception as e:
                print(f"Error stopping recording: {e}")
                tk.messagebox.showerror("Error", f"Failed to stop recording: {e}")


    def select_file(self):
        if self.vc is not None:
            filename = filedialog.askopenfilename(
                title="Select Video File",
                filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv"), ("All files", "*.*")]
            )
            if filename:
                try:
                    self.selected_file_entry.config(text=filename)
                    self.vc.set_video_path(filename)
                except Exception as e:
                    print(f"Error setting video path: {e}")
                    tk.messagebox.showerror("Error", f"Failed to load video file: {e}")

    def on_closing(self):
        if self.vc is not None:
            self.vc.close()
            if self.thread is not None:
                self.thread.join()
                self.thread = None
        root.destroy()

root = tk.Tk()
my_gui = WebCamCloneGUI(root)
root.mainloop()

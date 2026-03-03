import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
import cv2
from PIL import Image, ImageTk
import subprocess
import os
import sys
from WebCamClone import WebCamClone

class WebCamCloneGUI:
    def __init__(self, master):
        self.master = master
        master.title("WebCamClone GUI")
        
        # Set the window icon
        try:
            master.iconbitmap("wc.ico")
        except Exception as e:
            print(f"Could not load icon: {e}")

        self.vc = None
        self.thread = None
        self.preview_thread = None
        self.preview_running = False
        self.always_on_top = False
        self.preview_width = 220
        self.preview_height = 165
        self.virtual_camera_check_running = False

        # Preview frame - positioned on the right
        self.preview_frame = tk.Frame(master)
        self.preview_frame.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.Y)
        
        self.preview_label = tk.Label(self.preview_frame, text="Preview", font=("Arial", 8, "bold"))
        self.preview_label.pack(side=tk.TOP, pady=1)
        
        self.preview_canvas = tk.Label(self.preview_frame, bg="black", relief="sunken", bd=1)
        self.preview_canvas.pack(side=tk.TOP, pady=1)
        self.preview_placeholder = tk.PhotoImage(width=self.preview_width, height=self.preview_height)
        self.preview_canvas.config(image=self.preview_placeholder)
        self.preview_canvas.image = self.preview_placeholder
        self.playback_speed_var = tk.DoubleVar(value=1.0)
        self.playback_speed_frame = tk.Frame(self.preview_frame)
        self.playback_speed_label = tk.Label(self.playback_speed_frame, text="Playback Speed", font=("Arial", 8, "bold"))
        self.playback_speed_label.pack(side=tk.TOP, pady=(4, 0))
        self.playback_speed_value_label = tk.Label(self.playback_speed_frame, text="1.00x", font=("Arial", 8))
        self.playback_speed_value_label.pack(side=tk.TOP, pady=1)
        self.playback_speed_slider = tk.Scale(
            self.playback_speed_frame,
            from_=0.25,
            to=3.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            length=self.preview_width,
            showvalue=False,
            variable=self.playback_speed_var,
            command=self.on_playback_speed_changed
        )
        self.playback_speed_slider.pack(side=tk.TOP, pady=(0, 2))

        # Main controls frame - positioned on the left
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)

        
        # Feed controls frame
        self.feed_frame = tk.LabelFrame(self.main_frame, text="Feed Controls", font=("Arial", 8, "bold"), pady=5)
        self.feed_frame.pack(fill=tk.X, pady=3)

        self.live_feed_button = tk.Button(self.feed_frame, text="Live Feed", command=self.switch_to_webcam, width=12, height=1)
        self.live_feed_button.pack(side=tk.LEFT, padx=5)

        self.virtual_feed_button = tk.Button(self.feed_frame, text="Virtual Feed", command=self.validate_and_switch_to_video, state=tk.DISABLED, width=12, height=1)
        self.virtual_feed_button.pack(side=tk.LEFT, padx=5)

        # Recording controls frame
        self.record_frame = tk.LabelFrame(self.main_frame, text="Recording Controls", font=("Arial", 8, "bold"), pady=5)
        self.record_frame.pack(fill=tk.X, pady=3)

        self.record_button = tk.Button(self.record_frame, text="Start Recording", command=self.start_recording, state=tk.DISABLED, width=12, height=1)
        self.record_button.pack(side=tk.LEFT, padx=5)

        self.stop_record_button = tk.Button(self.record_frame, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED, width=12, height=1)
        self.stop_record_button.pack(side=tk.LEFT, padx=5)

        # Window settings frame
        self.window_frame = tk.LabelFrame(self.main_frame, text="Window Settings", font=("Arial", 8, "bold"), pady=5)
        self.window_frame.pack(fill=tk.X, pady=3)

        self.always_on_top_var = tk.BooleanVar()
        self.always_on_top_checkbox = tk.Checkbutton(self.window_frame, text="Always On Top", variable=self.always_on_top_var, command=self.toggle_always_on_top)
        self.always_on_top_checkbox.pack(side=tk.LEFT, padx=5)

        # Camera settings frame
        self.camera_frame = tk.LabelFrame(self.main_frame, text="Camera Settings", font=("Arial", 8, "bold"), pady=5)
        self.camera_frame.pack(fill=tk.X, pady=3)
        
        self.camera_label = tk.Label(self.camera_frame, text="Camera:")
        self.camera_label.pack(side=tk.LEFT, padx=5)
        
        self.camera_entry = tk.Spinbox(self.camera_frame, from_=0, to=10, width=4)
        self.camera_entry.delete(0, tk.END)
        self.camera_entry.insert(0, "0")  # Default to camera 0
        self.camera_entry.configure(command=self.on_camera_selection_changed)
        self.camera_entry.bind("<Return>", self.on_camera_selection_changed)
        self.camera_entry.bind("<FocusOut>", self.on_camera_selection_changed)
        self.camera_entry.pack(side=tk.LEFT, padx=5)


        # Status and info frame
        self.status_frame = tk.LabelFrame(self.main_frame, text="Status & Information", font=("Arial", 8, "bold"), pady=5)
        self.status_frame.pack(fill=tk.X, pady=3)

        self.selected_file_entry = tk.Label(self.status_frame, text="No Video File Selected", state=tk.NORMAL, font=("Arial", 8))
        self.selected_file_entry.pack(side=tk.TOP, padx=5, pady=2)

        self.status_label = tk.Label(self.status_frame, text="Ready", fg="green", font=("Arial", 9, "bold"))
        self.status_label.pack(side=tk.TOP, padx=5, pady=2)
        
        # Virtual camera status
        self.virtual_camera_status = tk.Label(self.status_frame, text="Virtual Camera: Checking...", fg="orange", font=("Arial", 8, "bold"))
        self.virtual_camera_status.pack(side=tk.TOP, padx=5, pady=2)
        
        # Install button frame (initially hidden)
        self.install_frame = tk.Frame(self.status_frame)
        self.install_button = tk.Button(self.install_frame, text="Install Webcam Clone Virtual Camera", 
                                      command=self.install_virtual_camera, width=25, height=1, 
                                      bg="lightblue", font=("Arial", 8, "bold"))
        self.install_button.pack(side=tk.TOP, padx=5, pady=2)
        
        # Instructions label
        self.instructions_label = tk.Label(self.status_frame, text="Instructions: Start Live Feed → Select Video File → Switch to Virtual Feed", 
                                         font=("Arial", 8), fg="gray", wraplength=300)
        self.instructions_label.pack(side=tk.TOP, padx=5, pady=2)
        
        # Recording info label
        self.recording_info_label = tk.Label(self.status_frame, text="Recording: Records whatever is currently being broadcast to virtual camera", 
                                           font=("Arial", 8), fg="purple", wraplength=300)
        self.recording_info_label.pack(side=tk.TOP, padx=5, pady=2)

        self.select_button = tk.Button(self.status_frame, text="Select Video File", command=self.select_file, state=tk.DISABLED, width=20, height=1)
        self.select_button.pack(side=tk.TOP, padx=5, pady=3)

        master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Check for virtual camera after UI is ready
        self.master.after(1000, self.check_virtual_camera_async)

    def check_virtual_camera_async(self):
        """Run virtual camera availability check in background."""
        if self.virtual_camera_check_running:
            return
        self.virtual_camera_check_running = True

        def run_check():
            try:
                self.check_virtual_camera()
            finally:
                self.virtual_camera_check_running = False

        Thread(target=run_check, daemon=True).start()

    def check_virtual_camera(self):
        """Check if Webcam Clone virtual camera is available"""
        try:
            # Try to create a test virtual camera instance
            try:
                import pyvirtualcam
                test_cam = pyvirtualcam.Camera(width=640, height=480, fps=30, device='Webcam Clone')
                test_cam.close()
                # If we get here, the virtual camera exists
                self.master.after(0, lambda: self.virtual_camera_status.config(text="Virtual Camera: 'Webcam Clone' Available", fg="green"))
                self.master.after(0, self.install_frame.pack_forget)  # Hide install button
            except Exception as e:
                # Virtual camera doesn't exist or can't be created
                self.master.after(0, lambda: self.virtual_camera_status.config(text="Virtual Camera: 'Webcam Clone' Not Found", fg="red"))
                self.master.after(0, lambda: self.install_frame.pack(side=tk.TOP, padx=5, pady=2))  # Show install button
                print(f"Virtual camera check failed: {e}")
        except ImportError:
            self.master.after(0, lambda: self.virtual_camera_status.config(text="Virtual Camera: pyvirtualcam not available", fg="red"))
            self.master.after(0, lambda: self.install_frame.pack(side=tk.TOP, padx=5, pady=2))

    def install_virtual_camera(self):
        """Install the Webcam Clone virtual camera"""
        try:
            # Get the directory where the script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            install_bat = os.path.join(script_dir, "Install_virtual_cam", "Install.bat")
            
            if not os.path.exists(install_bat):
                messagebox.showerror("Error", f"Install script not found: {install_bat}")
                return
            
            # Show installation dialog
            result = messagebox.askyesno("Install Virtual Camera", 
                "This will install the 'Webcam Clone' virtual camera.\n\n"
                "Administrator privileges are required.\n"
                "The installation process will open in a new window.\n\n"
                "Do you want to continue?")
            
            if result:
                # Update status
                self.virtual_camera_status.config(text="Virtual Camera: Installing...", fg="orange")
                self.install_button.config(state=tk.DISABLED, text="Installing...")
                
                # Run the install script
                subprocess.Popen([install_bat], shell=True)
                
                # Show completion message
                messagebox.showinfo("Installation Started", 
                    "Installation process has started.\n\n"
                    "Please wait for the installation to complete,\n"
                    "then restart this application to use the virtual camera.")
                
                # Reset button state
                self.install_button.config(state=tk.NORMAL, text="Install Webcam Clone Virtual Camera")
                
        except Exception as e:
            messagebox.showerror("Installation Error", f"Failed to start installation: {e}")
            self.virtual_camera_status.config(text="Virtual Camera: Installation Failed", fg="red")
            self.install_button.config(state=tk.NORMAL, text="Install Webcam Clone Virtual Camera")

    def start_vc(self):
        if self.vc is None:
            # Check if virtual camera is available first
            if "Not Found" in self.virtual_camera_status.cget("text") or "not available" in self.virtual_camera_status.cget("text"):
                messagebox.showwarning("Virtual Camera Not Available", 
                    "The 'Webcam Clone' virtual camera is not installed or not available.\n\n"
                    "Please install it using the 'Install Webcam Clone Virtual Camera' button,\n"
                    "then restart this application.")
                return
            
            # Show loading feedback
            self.live_feed_button.config(state=tk.DISABLED, text="Starting...")
            self.status_label.config(text="Creating virtual camera...", fg="orange")
            self.master.update()  # Force GUI update
            
            try:
                # Step 1: Create WebCamClone object with callback
                self.status_label.config(text="Initializing camera resources...", fg="orange")
                self.master.update()
                # Get camera number from input box
                camera_number = int(self.camera_entry.get())
                self.vc = WebCamClone(
                    camera_index=camera_number,
                    on_feed_started=lambda: self.master.after(0, self.on_feed_started_callback)
                )
                
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
                self.virtual_camera_status.config(text="Virtual Camera: Initialization Failed", fg="red")
                print(f"Error starting virtual camera: {e}")
                # Show error message to user
                tk.messagebox.showerror("Error", f"Failed to start virtual camera: {e}")

    def on_camera_selection_changed(self, event=None):
        """Switch camera immediately if live feed is already running."""
        try:
            camera_number = int(self.camera_entry.get())
        except ValueError:
            return

        if self.vc is None:
            return

        self.status_label.config(text=f"Switching to Camera {camera_number}...", fg="orange")
        self.master.update()
        switched = self.vc.switch_camera(camera_number)
        if switched:
            self.vc.switch_to_webcam()
            self.status_label.config(text=f"Live Feed Active - Camera {camera_number}", fg="green")
            self.virtual_camera_status.config(text="Virtual Camera: 'Webcam Clone' Broadcasting Camera", fg="green")
            self.instructions_label.config(text="✓ Live feed is now broadcasting your selected camera to 'Webcam Clone' virtual camera.")
            self.recording_info_label.config(text="Recording: Will record the camera feed being broadcast")
            self.hide_playback_speed_controls()
        else:
            self.status_label.config(text=f"Failed to open Camera {camera_number}", fg="red")
            tk.messagebox.showerror("Camera Switch Failed", f"Could not open camera index {camera_number}.")
    
    def on_feed_started_callback(self):
        """Called when the feed actually starts"""
        self.status_label.config(text="Live Feed Active - Virtual Camera Ready!", fg="green")
        self.virtual_camera_status.config(text="Virtual Camera: 'Webcam Clone' Initialized", fg="green")
        self.install_frame.pack_forget()  # Hide install button since virtual camera is working
        self.instructions_label.config(text="✓ Live feed is now broadcasting to 'Webcam Clone' virtual camera. You can select a video file to switch to virtual feed.")
        self.recording_info_label.config(text="Recording: Will record the camera feed being broadcast")
        self.hide_playback_speed_controls()
        # Start preview display
        self.start_preview()

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
                self.status_label.config(text="Live Feed Active - Camera Broadcasting!", fg="green")
                self.virtual_camera_status.config(text="Virtual Camera: 'Webcam Clone' Broadcasting Camera", fg="green")
                self.instructions_label.config(text="✓ Live feed is now broadcasting your camera to 'Webcam Clone' virtual camera.")
                self.recording_info_label.config(text="Recording: Will record the camera feed being broadcast")
                self.hide_playback_speed_controls()
            except Exception as e:
                print(f"Error switching to webcam: {e}")
                self.status_label.config(text="Error", fg="red")
                self.virtual_camera_status.config(text="Virtual Camera: Error", fg="red")
                tk.messagebox.showerror("Error", f"Failed to switch to webcam: {e}")

    def validate_and_switch_to_video(self):
        """Validate prerequisites before switching to virtual feed"""
        if self.vc is None:
            tk.messagebox.showwarning("No Live Feed", 
                "Please start the Live Feed first before switching to virtual feed.\n\n"
                "Steps:\n"
                "1. Click 'Live Feed' button\n"
                "2. Wait for 'Virtual Camera Ready' message\n"
                "3. Select a video file\n"
                "4. Then click 'Virtual Feed'")
            return
        
        # Check if video file is selected
        if not hasattr(self.vc, 'video') or self.vc.video is None:
            tk.messagebox.showwarning("No Video File Selected", 
                "Please select a video file first before switching to virtual feed.\n\n"
                "Steps:\n"
                "1. Click 'Select Video File' button\n"
                "2. Choose your video file\n"
                "3. Then click 'Virtual Feed'\n\n"
                "The video file will be broadcast to the 'Webcam Clone' virtual camera.")
            return
        
        # All validations passed, proceed with switching
        self.switch_to_video()
    
    def switch_to_video(self):
        """Switch to video feed (called after validation)"""
        try:
            self.vc.switch_to_video()
            self.vc.set_playback_speed(self.playback_speed_var.get())
            self.status_label.config(text="Virtual Feed Active - Video Broadcasting!", fg="blue")
            self.virtual_camera_status.config(text="Virtual Camera: 'Webcam Clone' Broadcasting Video", fg="blue")
            self.instructions_label.config(text="✓ Virtual feed is now broadcasting your video file to 'Webcam Clone' virtual camera.")
            self.recording_info_label.config(text="Recording: Will record the video file being broadcast")
            self.show_playback_speed_controls()
        except Exception as e:
            print(f"Error switching to video: {e}")
            self.status_label.config(text="Error", fg="red")
            self.virtual_camera_status.config(text="Virtual Camera: Error", fg="red")
            tk.messagebox.showerror("Error", f"Failed to switch to video: {e}")

    def on_playback_speed_changed(self, value):
        speed = float(value)
        self.playback_speed_value_label.config(text=f"{speed:.2f}x")
        if self.vc is not None:
            self.vc.set_playback_speed(speed)

    def show_playback_speed_controls(self):
        if not self.playback_speed_frame.winfo_ismapped():
            self.playback_speed_frame.pack(side=tk.TOP, fill=tk.X, pady=(2, 0))

    def hide_playback_speed_controls(self):
        if self.playback_speed_frame.winfo_ismapped():
            self.playback_speed_frame.pack_forget()

    def start_recording(self):
        if self.vc is not None:
            # Check if any feed is active
            if not self.is_feed_active():
                tk.messagebox.showwarning("No Active Feed", 
                    "Please start a feed before recording.\n\n"
                    "Steps:\n"
                    "1. Click 'Live Feed' to start camera feed, OR\n"
                    "2. Click 'Virtual Feed' to start video file feed\n"
                    "3. Then click 'Start Recording'")
                return
            
            filename = filedialog.asksaveasfilename(
                title="Save Recording As",
                defaultextension=".mp4",
                filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
            )
            if filename:
                try:
                    self.vc.start_recording(filename)
                    self.record_button.config(state=tk.DISABLED, text="Recording...")
                    self.stop_record_button.config(state=tk.NORMAL)
                    self.status_label.config(text="Recording Active - Saving to file!", fg="red")
                    self.recording_info_label.config(text=f"✓ Recording: {filename.split('/')[-1]} - Records current broadcast")
                except Exception as e:
                    print(f"Error starting recording: {e}")
                    tk.messagebox.showerror("Error", f"Failed to start recording: {e}")
        else:
            tk.messagebox.showwarning("No Feed Started", 
                "Please start a feed first before recording.\n\n"
                "Steps:\n"
                "1. Click 'Live Feed' button\n"
                "2. Wait for 'Virtual Camera Ready' message\n"
                "3. Then click 'Start Recording'")

    def stop_recording(self):
        if self.vc is not None:
            try:
                self.vc.stop_recording()
                self.record_button.config(state=tk.NORMAL, text="Start Recording")
                self.stop_record_button.config(state=tk.DISABLED)
                self.status_label.config(text="Recording Stopped - File Saved!", fg="orange")
                self.recording_info_label.config(text="✓ Recording completed and saved to file")
            except Exception as e:
                print(f"Error stopping recording: {e}")
                tk.messagebox.showerror("Error", f"Failed to stop recording: {e}")
    
    def is_feed_active(self):
        """Check if any feed is currently active"""
        if self.vc is None:
            return False
        # Check if we're using webcam or video
        return (self.vc.use_webcam and self.vc.cap is not None) or (not self.vc.use_webcam and self.vc.video is not None)

    def toggle_always_on_top(self):
        """Toggle the always on top state of the window"""
        self.always_on_top = self.always_on_top_var.get()
        
        if self.always_on_top:
            self.master.attributes('-topmost', True)
        else:
            self.master.attributes('-topmost', False)


    def select_file(self):
        if self.vc is not None:
            filename = filedialog.askopenfilename(
                title="Select Video File",
                filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv"), ("All files", "*.*")]
            )
            if filename:
                try:
                    # Show loading status
                    self.status_label.config(text="Loading video file...", fg="orange")
                    self.master.update()
                    
                    self.vc.set_video_path(filename)
                    
                    # Update UI with success
                    self.selected_file_entry.config(text=f"✓ {filename.split('/')[-1]}")
                    self.status_label.config(text="Video file loaded successfully!", fg="green")
                    self.instructions_label.config(text="✓ Video file loaded! You can now click 'Virtual Feed' to broadcast this video.")
                    
                except Exception as e:
                    print(f"Error setting video path: {e}")
                    self.status_label.config(text="Error loading video", fg="red")
                    tk.messagebox.showerror("Error", f"Failed to load video file: {e}")
        else:
            tk.messagebox.showwarning("No Live Feed", 
                "Please start the Live Feed first before selecting a video file.\n\n"
                "Steps:\n"
                "1. Click 'Live Feed' button\n"
                "2. Wait for 'Virtual Camera Ready' message\n"
                "3. Then select your video file")

    def start_preview(self):
        """Start the preview display thread"""
        if not self.preview_running and self.vc is not None:
            self.preview_running = True
            self.preview_thread = Thread(target=self.update_preview)
            self.preview_thread.daemon = True
            self.preview_thread.start()
    
    def stop_preview(self):
        """Stop the preview display"""
        self.preview_running = False
        if self.preview_thread is not None:
            self.preview_thread.join()
            self.preview_thread = None
    
    def update_preview(self):
        """Update the preview display with current frame"""
        while self.preview_running and self.vc is not None:
            try:
                frame = self.vc.get_current_frame()
                if frame is not None:
                    # Resize frame for preview
                    preview_frame = cv2.resize(frame, (self.preview_width, self.preview_height))
                    # Mirror the frame horizontally (like a webcam mirror)
                    preview_frame = cv2.flip(preview_frame, 1)
                    # Convert BGR to RGB for PIL
                    preview_frame = cv2.cvtColor(preview_frame, cv2.COLOR_BGR2RGB)
                    # Convert to PIL Image
                    image = Image.fromarray(preview_frame)
                    photo = ImageTk.PhotoImage(image)
                    # Update the canvas
                    self.preview_canvas.config(image=photo)
                    self.preview_canvas.image = photo  # Keep a reference
            except Exception as e:
                print(f"Preview error: {e}")
            # Update every 50ms (20 FPS)
            self.master.after(50, lambda: None)

    def on_closing(self):
        # Prevent multiple close attempts
        if hasattr(self, '_closing'):
            return
        self._closing = True
        
        # Disable the close button to prevent multiple clicks
        self.master.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Show closing status dialog
        self.show_closing_dialog()
        
        # Start shutdown process in a separate thread
        shutdown_thread = Thread(target=self.shutdown_process)
        shutdown_thread.daemon = True
        shutdown_thread.start()
    
    def show_closing_dialog(self):
        """Show a dialog with closing status"""
        self.closing_dialog = tk.Toplevel(self.master)
        self.closing_dialog.title("Closing WebCamClone")
        self.closing_dialog.geometry("300x150")
        self.closing_dialog.resizable(False, False)
        
        # Center the dialog
        self.closing_dialog.transient(self.master)
        self.closing_dialog.grab_set()
        
        # Make it modal
        self.closing_dialog.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable close button
        
        # Status label
        self.closing_status = tk.Label(self.closing_dialog, text="Shutting down...", font=("Arial", 10))
        self.closing_status.pack(pady=20)
        
        # Progress steps
        self.closing_steps = [
            "Stopping preview display...",
            "Stopping virtual camera...",
            "Releasing camera resources...",
            "Cleaning up threads...",
            "Closing application..."
        ]
        
        # Progress bar (simple text-based)
        self.progress_label = tk.Label(self.closing_dialog, text="", font=("Arial", 9), fg="blue")
        self.progress_label.pack(pady=10)
        
        # Cancel button (disabled during shutdown)
        self.cancel_button = tk.Button(self.closing_dialog, text="Cancel", state=tk.DISABLED, command=self.cancel_shutdown)
        self.cancel_button.pack(pady=10)
    
    def cancel_shutdown(self):
        """Cancel the shutdown process"""
        self.closing_dialog.destroy()
        self._closing = False
        # Re-enable close button
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def shutdown_process(self):
        """Perform the actual shutdown process with status updates"""
        try:
            # Step 1: Stop preview
            self.master.after(0, lambda: self.update_closing_status(0))
            self.stop_preview()
            
            # Step 2: Stop virtual camera
            self.master.after(0, lambda: self.update_closing_status(1))
            if self.vc is not None:
                self.vc.close()
                # Update virtual camera status
                self.master.after(0, lambda: self.virtual_camera_status.config(text="Virtual Camera: Shutting Down", fg="orange"))
            
            # Step 3: Release camera resources
            self.master.after(0, lambda: self.update_closing_status(2))
            
            # Step 4: Clean up threads
            self.master.after(0, lambda: self.update_closing_status(3))
            if self.thread is not None:
                self.thread.join(timeout=2)  # Wait max 2 seconds
                self.thread = None
            
            # Step 5: Close application
            self.master.after(0, lambda: self.update_closing_status(4))
            
            # Close the dialog and destroy the main window
            self.master.after(0, self.finalize_shutdown)
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
            self.master.after(0, self.finalize_shutdown)
    
    def update_closing_status(self, step):
        """Update the closing status display"""
        if hasattr(self, 'closing_status') and self.closing_status:
            self.closing_status.config(text=self.closing_steps[step])
            self.progress_label.config(text=f"Step {step + 1} of {len(self.closing_steps)}")
            self.master.update()
    
    def finalize_shutdown(self):
        """Finalize the shutdown process"""
        try:
            if hasattr(self, 'closing_dialog'):
                self.closing_dialog.destroy()
        except:
            pass
        root.destroy()

root = tk.Tk()
my_gui = WebCamCloneGUI(root)
root.mainloop()

import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
import cv2
from PIL import Image, ImageTk
from WebCamClone import WebCamClone

class WebCamCloneGUI:
    def __init__(self, master):
        self.master = master
        master.title("WebCamClone GUI")

        self.vc = None
        self.thread = None
        self.preview_thread = None
        self.preview_running = False

        # Preview frame - smaller and positioned on the right
        self.preview_frame = tk.Frame(master)
        self.preview_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)
        
        self.preview_label = tk.Label(self.preview_frame, text="Preview", font=("Arial", 9, "bold"))
        self.preview_label.pack(side=tk.TOP, pady=2)
        
        self.preview_canvas = tk.Label(self.preview_frame, bg="black", relief="sunken", bd=1)
        self.preview_canvas.pack(side=tk.TOP, pady=2)

        # Main controls frame - positioned on the left
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.top_frame = tk.Frame(self.main_frame)
        self.top_frame.pack(pady=5)

        self.middle_frame = tk.Frame(self.main_frame)
        self.middle_frame.pack(pady=5)

        self.bottom_frame = tk.Frame(self.main_frame)
        self.bottom_frame.pack(pady=5)

        # Camera selection frame
        self.camera_frame = tk.Frame(self.main_frame)
        self.camera_frame.pack(pady=5)
        
        self.camera_label = tk.Label(self.camera_frame, text="Camera Number:")
        self.camera_label.pack(side=tk.LEFT, padx=5)
        
        self.camera_entry = tk.Spinbox(self.camera_frame, from_=0, to=10, width=5)
        self.camera_entry.delete(0, tk.END)
        self.camera_entry.insert(0, "0")  # Default to camera 0
        self.camera_entry.pack(side=tk.LEFT, padx=5)

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
                # Get camera number from input box
                camera_number = int(self.camera_entry.get())
                self.vc = WebCamClone(camera_index=camera_number, on_feed_started=self.on_feed_started_callback)
                
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
                    # Resize frame for preview (smaller size - 100x75)
                    preview_frame = cv2.resize(frame, (180, 135))
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
            # Update every 50ms (20 FPS) - less frequent for smaller preview
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

import cv2
import pyvirtualcam
import sys
import time
from threading import Lock, Thread

class WebCamClone:
    def __init__(self, width=640, height=480, fps=30, video_path=None, camera_index=0, on_feed_started=None):
        self.width = width
        self.height = height
        self.fps = fps
        self.video_path = video_path
        self.camera_index = camera_index
        self.on_feed_started = on_feed_started  # Callback function
        # Lazy initialization - only create when needed
        self.cam = None
        self.cap = None
        self.video = None
        self.use_webcam = True
        self.isWebcamCloneRunning = False
        self.isRecording = False
        self.out = None
        self._initialized = False
        self.current_frame = None  # Store current frame for preview
        self.cap_lock = Lock()
        self.video_lock = Lock()
        self.video_source_fps = float(fps)
        self.playback_speed = 1.0
        self.video_frame_interval = 1.0 / float(fps) if fps > 0 else (1.0 / 30.0)
        self.last_video_frame_time = 0.0
        self.current_video_frame = None

    def _update_video_interval(self):
        base_fps = self.video_source_fps if self.video_source_fps > 0 else float(self.fps)
        effective_fps = base_fps * self.playback_speed
        if effective_fps <= 0:
            effective_fps = float(self.fps) if self.fps > 0 else 30.0
        self.video_frame_interval = 1.0 / effective_fps

    def _open_camera_capture(self, camera_index):
        """Open physical camera with backend strategy tuned per platform."""
        if sys.platform.startswith("win"):
            # Try DSHOW first for faster startup on many Windows drivers,
            # then MSMF as fallback for compatibility.
            backends = []
            if hasattr(cv2, "CAP_DSHOW"):
                backends.append(cv2.CAP_DSHOW)
            if hasattr(cv2, "CAP_MSMF"):
                backends.append(cv2.CAP_MSMF)
            backends.append(cv2.CAP_ANY)
        else:
            backends = [cv2.CAP_ANY]

        for backend in backends:
            cap = cv2.VideoCapture(camera_index, backend)
            if cap.isOpened():
                # Ask the driver for the target output format to reduce per-frame scaling work.
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                cap.set(cv2.CAP_PROP_FPS, self.fps)
                if hasattr(cv2, "CAP_PROP_BUFFERSIZE"):
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                return cap
            cap.release()
        return None

    def set_live_feed_camera(self, camera_index):
        self.camera_index = camera_index

    def set_virtual_camera(self, virtual_camera_index):
        self.virtual_camera_index = virtual_camera_index


    def switch_feed(self):
        self.use_webcam = not self.use_webcam
    
    def switch_to_webcam(self):
        self.use_webcam = True
    
    def switch_to_video(self):
        self.use_webcam = False
        self.last_video_frame_time = 0.0

    def set_playback_speed(self, speed):
        """Set virtual video playback speed multiplier."""
        try:
            speed_value = float(speed)
        except (ValueError, TypeError):
            return
        speed_value = max(0.25, min(3.0, speed_value))
        with self.video_lock:
            self.playback_speed = speed_value
            self._update_video_interval()

    def set_video_path(self, video_path):
        self.video_path = video_path
        with self.video_lock:
            # Release previous video capture if present.
            if self.video is not None:
                self.video.release()
                self.video = None

            # Only initialize video capture if path is valid.
            if not video_path:
                self.current_video_frame = None
                return

            video = cv2.VideoCapture(self.video_path)
            if not video.isOpened():
                video.release()
                raise Exception(f"Could not open video file: {self.video_path}")

            source_fps = float(video.get(cv2.CAP_PROP_FPS))
            if source_fps <= 1.0 or source_fps > 240.0:
                source_fps = float(self.fps)
            self.video_source_fps = source_fps
            self._update_video_interval()
            self.last_video_frame_time = 0.0
            self.current_video_frame = None

            # Probe a few frames to validate the stream is decodable.
            probe_ok = False
            for _ in range(10):
                ret, _ = video.read()
                if ret:
                    probe_ok = True
                    break
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            if not probe_ok:
                video.release()
                raise Exception("Video file appears corrupted or unsupported.")

            self.video = video

    def switch_camera(self, camera_index):
        """Switch active physical camera while running."""
        if camera_index == self.camera_index and self.cap is not None:
            return True

        new_cap = self._open_camera_capture(camera_index)
        if new_cap is None:
            return False

        with self.cap_lock:
            old_cap = self.cap
            self.cap = new_cap
            self.camera_index = camera_index
            self.current_frame = None

        if old_cap is not None:
            old_cap.release()
        return True

    def _initialize_resources(self):
        """Initialize camera and virtual camera resources"""
        if self._initialized:
            return True
            
        try:
            init_start = time.perf_counter()
            timing = {}
            results = {"cam": None, "cap": None}
            errors = {"cam": None, "cap": None}

            def init_virtual_camera():
                start = time.perf_counter()
                try:
                    results["cam"] = pyvirtualcam.Camera(
                        width=self.width,
                        height=self.height,
                        fps=self.fps,
                        device='Webcam Clone'
                    )
                except Exception as e:
                    errors["cam"] = e
                finally:
                    timing["virtual_cam"] = time.perf_counter() - start

            def init_webcam():
                start = time.perf_counter()
                try:
                    results["cap"] = self._open_camera_capture(self.camera_index)
                except Exception as e:
                    errors["cap"] = e
                finally:
                    timing["webcam"] = time.perf_counter() - start

            virtual_thread = Thread(target=init_virtual_camera, daemon=True)
            webcam_thread = Thread(target=init_webcam, daemon=True)
            virtual_thread.start()
            webcam_thread.start()
            virtual_thread.join()
            webcam_thread.join()

            if errors["cam"] is not None:
                raise errors["cam"]
            if errors["cap"] is not None:
                raise errors["cap"]

            self.cam = results["cam"]
            self.cap = results["cap"]
            if self.cap is None:
                if self.cam is not None:
                    self.cam.close()
                    self.cam = None
                raise Exception("Could not open webcam")
            # Initialize video capture if path is provided
            if self.video_path:
                self.video = cv2.VideoCapture(self.video_path)
                if not self.video.isOpened():
                    print(f"Warning: Could not open video file: {self.video_path}")
                    self.video = None

            total_time = time.perf_counter() - init_start
            print(
                "Init timing (s): "
                f"virtual_cam={timing.get('virtual_cam', 0.0):.2f}, "
                f"webcam={timing.get('webcam', 0.0):.2f}, "
                f"total={total_time:.2f}"
            )
            
            self._initialized = True
            return True
        except Exception as e:
            print(f"Error initializing resources: {e}")
            return False
    
    def startWebcamClone(self):
        # Initialize resources before starting
        if not self._initialize_resources():
            print("Failed to initialize resources")
            return
            
        self.isWebcamCloneRunning = True
        
        # Call the callback to notify GUI that feed has started
        if self.on_feed_started:
            self.on_feed_started()
            
        while self.isWebcamCloneRunning:
            self.send_frame()

    def send_frame(self):
        if not self._initialized:
            time.sleep(0.005)
            return

        frame_bgr = None

        if self.use_webcam:
            with self.cap_lock:
                if self.cap is None:
                    time.sleep(0.01)
                    return
                ret, frame = self.cap.read()
            if ret:
                frame_bgr = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_AREA)
        else:
            frame = None
            with self.video_lock:
                if self.video is None:
                    time.sleep(0.01)
                    return
                now = time.perf_counter()
                should_advance = (
                    self.current_video_frame is None or
                    (now - self.last_video_frame_time) >= self.video_frame_interval
                )

                if should_advance:
                    ret, next_frame = self.video.read()
                    if ret:
                        self.current_video_frame = next_frame
                        self.last_video_frame_time = now
                    else:
                        frame_count = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
                        current_pos = int(self.video.get(cv2.CAP_PROP_POS_FRAMES))
                        if frame_count > 0 and current_pos >= frame_count - 1:
                            # Restart only at end-of-file.
                            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        elif frame_count > 0:
                            # Skip likely-corrupt frame to avoid decode-error loops.
                            self.video.set(cv2.CAP_PROP_POS_FRAMES, min(current_pos + 1, frame_count - 1))
                if self.current_video_frame is not None:
                    frame = self.current_video_frame.copy()

            if frame is not None:
                frame_bgr = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_AREA)

        if frame_bgr is None:
            # Avoid busy-spinning when no frame is available.
            time.sleep(0.005)
            return

        # Keep BGR for recording/preview, convert once for virtual cam send.
        self.current_frame = frame_bgr
        if self.isRecording and self.out is not None:
            self.out.write(frame_bgr)

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        self.cam.send(frame_rgb)
        self.cam.sleep_until_next_frame()

    def start_recording(self, filename):
        # define the codec and create a VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(filename, fourcc, self.fps, (self.width, self.height))
        # set the isRecording flag to True
        self.isRecording = True

    def stop_recording(self):
        # set the isRecording flag to False
        self.isRecording = False
        # release the VideoWriter object
        if self.out is not None:
            self.out.release()
            self.out = None
    
    def get_current_frame(self):
        """Get the current frame for preview display"""
        return self.current_frame


    def close(self):
        # stop recording and release resources
        self.stop_recording()
        # stop sending frames and release resources
        self.isWebcamCloneRunning = False
        # release resources for webcam and video feeds
        with self.cap_lock:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
        with self.video_lock:
            if self.video is not None:
                self.video.release()
                self.video = None
        if self.cam is not None:
            self.cam.close()
        self._initialized = False

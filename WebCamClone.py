import cv2
import pyvirtualcam

class WebCamClone:
    def __init__(self, width=640, height=480, fps=30, video_path=None, on_feed_started=None):
        self.width = width
        self.height = height
        self.fps = fps
        self.video_path = video_path
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

    def set_live_feed_camera(self, camera_index):
        self.live_feed_camera_index = camera_index

    def set_virtual_camera(self, virtual_camera_index):
        self.virtual_camera_index = virtual_camera_index


    def switch_feed(self):
        self.use_webcam = not self.use_webcam
    
    def switch_to_webcam(self):
        self.use_webcam = True
    
    def switch_to_video(self):
        self.use_webcam = False

    def set_video_path(self, video_path):
        self.video_path = video_path
        # Only initialize video capture if path is valid
        if video_path:
            self.video = cv2.VideoCapture(self.video_path)
        else:
            self.video = None

    def _initialize_resources(self):
        """Initialize camera and virtual camera resources"""
        if self._initialized:
            return True
            
        try:
            # Initialize virtual camera
            self.cam = pyvirtualcam.Camera(width=self.width, height=self.height, fps=self.fps, device='Webcam Clone')
            # Initialize webcam
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open webcam")
            # Initialize video capture if path is provided
            if self.video_path:
                self.video = cv2.VideoCapture(self.video_path)
                if not self.video.isOpened():
                    print(f"Warning: Could not open video file: {self.video_path}")
                    self.video = None
            
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
            return
            
        if self.use_webcam:
            if self.cap is None:
                return
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (self.width, self.height))
                if self.isRecording:
                    # write the frame to the output file
                    self.out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                self.cam.send(frame)
                self.cam.sleep_until_next_frame()
        else:
            if self.video is None:
                return
            ret, frame = self.video.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (self.width, self.height))
               
                self.cam.send(frame)
                self.cam.sleep_until_next_frame()
            else:
                # restart the video when it ends
                self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)

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


    def close(self):
        # stop recording and release resources
        self.stop_recording()
        # stop sending frames and release resources
        self.isWebcamCloneRunning = False
        # release resources for webcam and video feeds
        if self.cap is not None:
            self.cap.release()
        if self.video is not None:
            self.video.release()
        if self.cam is not None:
            self.cam.close()
        self._initialized = False

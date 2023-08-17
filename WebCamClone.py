import cv2
import pyvirtualcam

class WebCamClone:
    def __init__(self, width=640, height=480, fps=30, video_path=None):
        self.width = width
        self.height = height
        self.fps = fps
        self.video_path = video_path
        self.cam = pyvirtualcam.Camera(width=self.width, height=self.height, fps=self.fps, device='Webcam Clone7')
        self.cap = cv2.VideoCapture(0)
        self.video = cv2.VideoCapture(self.video_path)
        self.use_webcam = True
        self.isWebcamCloneRunning = False
        self.isRecording = False
        self.out = None

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
        self.video = cv2.VideoCapture(self.video_path)

    def startWebcamClone(self):
        self.isWebcamCloneRunning = True
        while self.isWebcamCloneRunning:
            self.send_frame()

    def send_frame(self):
        if self.use_webcam:
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
        self.cap.release()
        self.video.release()

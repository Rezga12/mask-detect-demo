from aiortc import MediaStreamTrack
import cv2
from av import VideoFrame


class OpenCVStreamTrack(MediaStreamTrack):

    kind = 'video'

    def __init__(self, track, mode):
        super().__init__()
        self.track = track
        self.mode = mode

    async def recv(self):

        frame = await self.track.recv()
        while not self.track._queue.empty():
            frame = await self.track.recv()

        if self.mode == 'regular':
            return frame

        img = frame.to_ndarray(format="bgr24")

        # prepare color
        img_color = cv2.pyrDown(cv2.pyrDown(img))
        for _ in range(6):
            img_color = cv2.bilateralFilter(img_color, 9, 9, 7)
        img_color = cv2.pyrUp(cv2.pyrUp(img_color))

        # prepare edges
        img_edges = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img_edges = cv2.adaptiveThreshold(
            cv2.medianBlur(img_edges, 7),
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            9,
            2,
        )
        img_edges = cv2.cvtColor(img_edges, cv2.COLOR_GRAY2RGB)

        # combine color and edges
        img = cv2.bitwise_and(img_color, img_edges)

        # rebuild a VideoFrame, preserving timing information
        new_frame = VideoFrame.from_ndarray(img, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base

        return new_frame


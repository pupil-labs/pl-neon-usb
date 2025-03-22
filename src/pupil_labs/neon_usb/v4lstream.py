from fcntl import ioctl
from select import select

from pyrav4l2.stream import Stream
from pyrav4l2.v4l2 import *


class V4lStream(Stream):
    def open(self):
        if self.f_cam.closed:
            self._open()

        ioctl(self.f_cam, VIDIOC_STREAMON, ctypes.c_int(V4L2_BUF_TYPE_VIDEO_CAPTURE))
        select((self.f_cam,), (), ())

    def close(self):
        self.f_cam.close()

    def get_frame(self):
        try:
            buf = self.buffers[0][0]
            ioctl(self.f_cam, VIDIOC_DQBUF, buf)

            frame = self.buffers[buf.index][1][: buf.bytesused]
            ioctl(self.f_cam, VIDIOC_QBUF, buf)

            return frame
        except:
            self._stop()

import ctypes
from fcntl import ioctl
from select import select
from typing import Any

from pyrav4l2 import v4l2
from pyrav4l2.stream import Stream


class V4lStream(Stream):
    def open(self) -> None:
        if self.f_cam.closed:
            self._open()

        ioctl(
            self.f_cam,
            v4l2.VIDIOC_STREAMON,
            ctypes.c_int(v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE),
        )
        select((self.f_cam,), (), ())

    def close(self) -> None:
        self.f_cam.close()

    def get_frame(self) -> Any | None:
        try:
            buf = self.buffers[0][0]
            ioctl(self.f_cam, v4l2.VIDIOC_DQBUF, buf)
            assert buf.index is not None
            frame = self.buffers[buf.index][1][: buf.bytesused]
            ioctl(self.f_cam, v4l2.VIDIOC_QBUF, buf)
        except Exception:
            self._stop()
            return None
        return frame

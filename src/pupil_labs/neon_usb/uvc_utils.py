import ctypes
from fcntl import ioctl

from pyrav4l2 import v4l2

UVC_RC_UNDEFINED = 0x00
UVC_SET_CUR = 0x01
UVC_GET_CUR = 0x81
UVC_GET_MIN = 0x82
UVC_GET_MAX = 0x83
UVC_GET_RES = 0x84
UVC_GET_LEN = 0x85
UVC_GET_INFO = 0x86
UVC_GET_DEF = 0x87

XU_CTL_EXPOSURE1 = 0x01
XU_CTL_EXPOSURE2 = 0x02
XU_CTL_GAIN1 = 0x03
XU_CTL_GAIN2 = 0x04


class uvc_xu_control_query(ctypes.Structure):
    _fields_ = [
        ("unit", ctypes.c_uint8),
        ("selector", ctypes.c_uint8),
        ("query", ctypes.c_uint8),
        ("size", ctypes.c_uint16),
        ("data", ctypes.POINTER(ctypes.c_uint8)),
    ]

    def __init__(self, unit, selector, query, size, data):
        self.unit = unit
        self.selector = selector
        self.query = query
        self.size = size

        d = ctypes.c_ubyte(int(data))
        self.data = ctypes.pointer(d)


UVCIOC_CTRL_QUERY = v4l2._IOWR("u", 0x21, uvc_xu_control_query)

size_map = {
    XU_CTL_EXPOSURE1: 4,
    XU_CTL_EXPOSURE2: 4,
    XU_CTL_GAIN1: 2,
    XU_CTL_GAIN2: 2,
}


def xu_query(fd, selector, control, data, data_len):
    query = uvc_xu_control_query(3, selector, control, data_len, data)

    return ioctl(fd, UVCIOC_CTRL_QUERY, query)


def xu_set(fd, selector, control, value):
    return xu_query(fd, selector, control, value, size_map[selector])


def set_eye_exposure(fd, eye_idx, value):
    try:
        xu_set(fd, XU_CTL_EXPOSURE1 + eye_idx, UVC_SET_CUR, value)
    except:
        print("Failed to set eye exposure")

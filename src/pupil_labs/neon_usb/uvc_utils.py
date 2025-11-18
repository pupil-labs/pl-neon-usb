import ctypes
from fcntl import ioctl
from io import TextIOWrapper
from typing import Any, ClassVar

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
    _fields_: ClassVar = [
        ("unit", ctypes.c_uint8),
        ("selector", ctypes.c_uint8),
        ("query", ctypes.c_uint8),
        ("size", ctypes.c_uint16),
        ("data", ctypes.POINTER(ctypes.c_uint8)),
    ]

    def __init__(
        self, unit: int, selector: int, query: int, size: int, data: Any
    ) -> None:
        self.unit = unit
        self.selector = selector
        self.query = query
        self.size = size

        # For set operations, data is an int; for get operations, it's already a pointer
        if isinstance(data, int):
            d = ctypes.c_ubyte(data)
            self.data = ctypes.pointer(d)
        else:
            self.data = data


UVCIOC_CTRL_QUERY = v4l2._IOWR("u", 0x21, uvc_xu_control_query)

size_map = {
    XU_CTL_EXPOSURE1: 4,
    XU_CTL_EXPOSURE2: 4,
    XU_CTL_GAIN1: 2,
    XU_CTL_GAIN2: 2,
}


def xu_query(
    fd: TextIOWrapper, selector: int, control: int, data: int, data_len: int
) -> Any:
    query = uvc_xu_control_query(3, selector, control, data_len, data)

    return ioctl(fd, UVCIOC_CTRL_QUERY, query)


def xu_set(fd: TextIOWrapper, selector: int, control: int, value: int) -> Any:
    return xu_query(fd, selector, control, value, size_map[selector])


def set_eye_exposure(fd: TextIOWrapper, eye_idx: int, value: int) -> Any:
    try:
        return xu_set(fd, XU_CTL_EXPOSURE1 + eye_idx, UVC_SET_CUR, value)
    except Exception:
        print("Failed to set eye exposure")
    return None


def get_eye_exposure(fd: TextIOWrapper, eye_idx: int) -> int | None:
    try:
        selector = XU_CTL_EXPOSURE1 + eye_idx
        data_len = size_map[selector]
        data_buffer = (ctypes.c_uint8 * data_len)()
        query = uvc_xu_control_query(
            unit=3,
            selector=selector,
            query=UVC_GET_CUR,
            size=data_len,
            data=ctypes.cast(data_buffer, ctypes.POINTER(ctypes.c_uint8)),
        )
        ioctl(fd, UVCIOC_CTRL_QUERY, query)
        value = int.from_bytes(bytes(data_buffer), byteorder="little")
    except Exception as e:
        print(f"Failed to get eye exposure: {e}")
        return None
    return value

import usb.core
import usb.util

from pupil_labs.neon_recording.calib import Calibration

VC_READ_CALIRATION_DATA = 0xD4
CALIBRATION_DATA_LENGTH = 1024
CALIBRATION_DATA_CHUNK_SIZE = 64
USB_ID_VENDOR = 0x16D0
USB_ID_PRODUCT = 0x11D3


def _read_calibration_data_chunk(dev: usb.core.Device, offset: int) -> bytes:
    """Read calibration data chunk from device

    Args:
        dev: the pyusb device to read from
        offset: the offset in bytes to read from

    Returns:
        the data chunk as byte array

    """
    data = dev.ctrl_transfer(
        usb.util.CTRL_IN | usb.util.CTRL_TYPE_VENDOR,
        VC_READ_CALIRATION_DATA,
        wIndex=offset,
        data_or_wLength=CALIBRATION_DATA_CHUNK_SIZE,
    )
    if len(data) != CALIBRATION_DATA_CHUNK_SIZE:
        raise OSError("Reading 64 bytes from VC_READ_CALIRATION_DATA failed")

    return bytes(data)


def _read_calibration_data(dev: usb.core.Device | None = None) -> bytes:
    """Read full calibration data block from device

    Arguments:
        dev: the pyusb device to read from

    Returns:
        byte array containing the calibration data

    """
    if dev is None:
        dev = _find_neon()

    data = b"".join([
        _read_calibration_data_chunk(dev, offset)
        for offset in range(0, CALIBRATION_DATA_LENGTH, CALIBRATION_DATA_CHUNK_SIZE)
    ])

    return data


def _find_neon() -> usb.core.Device:
    return usb.core.find(idVendor=USB_ID_VENDOR, idProduct=USB_ID_PRODUCT)


def get_calibration() -> Calibration:
    data = _read_calibration_data()
    return Calibration.from_buffer(data[: Calibration.dtype.itemsize])

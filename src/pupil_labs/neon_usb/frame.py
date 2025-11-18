from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class Frame:
    img: np.ndarray
    timestamp: float
    index: int

    @property
    def gray(self) -> np.ndarray:
        """Return a grayscale version of self.img"""
        if self.img.ndim == 2:  # already grayscale
            return self.img
        if self.img.shape[2] == 3:  # assume RGB or BGR
            # If it's RGB, conversion still works but yields correct grayscale
            return cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        raise ValueError("Unsupported image format for grayscale conversion")

    @property
    def bgr(self) -> np.ndarray:
        """Return a 3-channel BGR version of self.img"""
        if self.img.ndim == 2:  # grayscale -> BGR
            return cv2.cvtColor(self.img, cv2.COLOR_GRAY2BGR)
        if self.img.shape[2] == 3:
            return self.img
        raise ValueError("Unsupported image format for BGR conversion")

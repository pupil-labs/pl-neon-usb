"""pupil_labs.neon_usb package.

Library for connecting to Neon via USB
"""
from __future__ import annotations

import importlib.metadata

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

__all__: list[str] = ["__version__"]

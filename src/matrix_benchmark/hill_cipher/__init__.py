"""Sequential Hill Cipher functionality, isolated from matrix benchmarks."""

from .core import decrypt, encrypt
from .key import Key, inverse_key, validate_key

__all__ = ["Key", "decrypt", "encrypt", "inverse_key", "validate_key"]

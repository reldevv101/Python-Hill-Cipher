"""Validation and modular inverse operations for 2x2 Hill Cipher keys."""

from __future__ import annotations

from collections.abc import Sequence
from math import gcd

from .alphabet import MODULUS

Key = tuple[tuple[int, int], tuple[int, int]]


def validate_key(key: Sequence[Sequence[int]]) -> Key:
    """Return a normalized immutable key and reject keys without an inverse."""

    if len(key) != 2 or any(len(row) != 2 for row in key):
        raise ValueError("Kunci Hill Cipher harus berupa matriks 2 x 2.")
    if any(
        not isinstance(value, int) or isinstance(value, bool) or value < 0 or value >= MODULUS
        for row in key
        for value in row
    ):
        raise ValueError("Setiap elemen kunci harus berupa bilangan bulat dari 0 sampai 25.")

    normalized: Key = ((key[0][0], key[0][1]), (key[1][0], key[1][1]))
    determinant = (normalized[0][0] * normalized[1][1] - normalized[0][1] * normalized[1][0]) % MODULUS
    if gcd(determinant, MODULUS) != 1:
        raise ValueError(
            "Kunci tidak memiliki invers modulo 26. Pastikan gcd(determinan, 26) = 1."
        )
    return normalized


def inverse_key(key: Sequence[Sequence[int]]) -> Key:
    """Compute the inverse key matrix modulo 26."""

    validated = validate_key(key)
    a, b = validated[0]
    c, d = validated[1]
    determinant = (a * d - b * c) % MODULUS
    inverse_determinant = pow(determinant, -1, MODULUS)
    return (
        ((d * inverse_determinant) % MODULUS, (-b * inverse_determinant) % MODULUS),
        ((-c * inverse_determinant) % MODULUS, (a * inverse_determinant) % MODULUS),
    )

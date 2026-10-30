"""Sequential Hill Cipher encryption and decryption using modular integers."""

from __future__ import annotations

from collections.abc import Sequence

from .alphabet import MODULUS, normalize_plaintext, numbers_to_text, text_to_numbers
from .key import Key, inverse_key, validate_key


def _transform(text: str, key: Key) -> str:
    values = text_to_numbers(text)
    transformed: list[int] = []
    for offset in range(0, len(values), 2):
        first, second = values[offset : offset + 2]
        transformed.extend(
            (
                (key[0][0] * first + key[0][1] * second) % MODULUS,
                (key[1][0] * first + key[1][1] * second) % MODULUS,
            )
        )
    return numbers_to_text(transformed)


def transform_blocks(text: str, key: Sequence[Sequence[int]]) -> str:
    """Transform a prepared, even-length A-Z string using a 2x2 key."""

    matrix = validate_key(key)
    if any(character < "A" or character > "Z" for character in text):
        raise ValueError("Teks blok harus berisi huruf kapital A-Z saja.")
    if len(text) % 2:
        raise ValueError("Teks blok harus memiliki panjang genap.")
    return _transform(text, matrix)


def encrypt(plaintext: str, key: Sequence[Sequence[int]]) -> str:
    """Encrypt normalized A-Z text in two-letter blocks.

    Plaintext is uppercased and characters outside ASCII A-Z are discarded.
    An ``X`` is appended when the normalized text has odd length. The returned
    ciphertext does not carry the original length, so callers should retain
    the normalized plaintext length when they need to remove padding later.
    """

    matrix = validate_key(key)
    normalized = normalize_plaintext(plaintext)
    if len(normalized) % 2:
        normalized += "X"
    return _transform(normalized, matrix)


def decrypt(
    ciphertext: str,
    key: Sequence[Sequence[int]],
    *,
    original_length: int | None = None,
) -> str:
    """Decrypt A-Z ciphertext; optionally trim padding using its known length.

    Hill Cipher ciphertext is transformed in pairs. If ``original_length`` is
    omitted, any padding character remains in the result because it cannot be
    distinguished safely from a real trailing X.
    """

    matrix = inverse_key(key)
    if not isinstance(ciphertext, str):
        raise TypeError("Ciphertext harus berupa teks.")
    if any(character < "A" or character > "Z" for character in ciphertext):
        raise ValueError("Ciphertext harus berisi huruf kapital A-Z saja.")
    if len(ciphertext) % 2:
        raise ValueError("Panjang ciphertext harus genap.")
    if original_length is not None and (
        not isinstance(original_length, int)
        or isinstance(original_length, bool)
        or original_length < 0
        or original_length > len(ciphertext)
    ):
        raise ValueError("Panjang plaintext asli tidak valid untuk ciphertext ini.")

    plaintext = _transform(ciphertext, matrix)
    return plaintext if original_length is None else plaintext[:original_length]

"""A-Z alphabet conversion and plaintext normalization for Hill Cipher."""

from __future__ import annotations

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MODULUS = len(ALPHABET)


def normalize_plaintext(text: str) -> str:
    """Keep ASCII letters A-Z and uppercase them; discard all other characters."""

    if not isinstance(text, str):
        raise TypeError("Plaintext harus berupa teks.")
    return "".join(character for character in text.upper() if "A" <= character <= "Z")


def text_to_numbers(text: str) -> list[int]:
    """Convert an A-Z string to integers where A=0 and Z=25."""

    if any(character < "A" or character > "Z" for character in text):
        raise ValueError("Teks hanya boleh berisi huruf A-Z.")
    return [ord(character) - ord("A") for character in text]


def numbers_to_text(numbers: list[int]) -> str:
    """Convert integer alphabet positions to uppercase A-Z characters."""

    if any(not isinstance(number, int) or isinstance(number, bool) for number in numbers):
        raise TypeError("Nilai alfabet harus berupa bilangan bulat.")
    if any(number < 0 or number >= MODULUS for number in numbers):
        raise ValueError("Nilai alfabet harus berada pada rentang 0 sampai 25.")
    return "".join(chr(number + ord("A")) for number in numbers)

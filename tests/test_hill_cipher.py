"""Tests for the isolated sequential Hill Cipher implementation."""

from __future__ import annotations

import unittest

from hill_cipher_benchmark import decrypt, encrypt, inverse_key, validate_key
from hill_cipher_benchmark.alphabet import normalize_plaintext, numbers_to_text, text_to_numbers


class HillCipherAlphabetTests(unittest.TestCase):
    def test_normalizes_to_uppercase_ascii_letters(self) -> None:
        self.assertEqual(normalize_plaintext("Hello, World! 123"), "HELLOWORLD")

    def test_converts_letters_to_numbers_and_back(self) -> None:
        self.assertEqual(text_to_numbers("AZ"), [0, 25])
        self.assertEqual(numbers_to_text([0, 25]), "AZ")

    def test_rejects_non_ascii_letters_in_number_conversion(self) -> None:
        with self.assertRaises(ValueError):
            text_to_numbers("A!")


class HillCipherKeyTests(unittest.TestCase):
    def test_accepts_invertible_key_and_computes_inverse(self) -> None:
        key = ((3, 3), (2, 5))
        self.assertEqual(validate_key(key), key)
        self.assertEqual(inverse_key(key), ((15, 17), (20, 9)))

    def test_rejects_wrong_key_shape(self) -> None:
        with self.assertRaises(ValueError):
            validate_key(((1, 2, 3), (4, 5, 6)))

    def test_rejects_non_integer_or_out_of_range_key_values(self) -> None:
        for key in (((1, 2), (3, 26)), ((1, 2), (3, 4.0)), ((1, True), (3, 4))):
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_key(key)

    def test_rejects_key_without_modular_inverse(self) -> None:
        with self.assertRaises(ValueError):
            validate_key(((2, 0), (0, 1)))


class HillCipherCoreTests(unittest.TestCase):
    KEY = ((3, 3), (2, 5))

    def test_encrypts_known_vector(self) -> None:
        self.assertEqual(encrypt("HELP", self.KEY), "HIAT")

    def test_normalizes_and_pads_odd_length_plaintext(self) -> None:
        ciphertext = encrypt("Hello!", self.KEY)
        self.assertEqual(len(ciphertext), 6)
        self.assertEqual(decrypt(ciphertext, self.KEY, original_length=5), "HELLO")

    def test_decryption_keeps_padding_without_original_length(self) -> None:
        ciphertext = encrypt("CAT", self.KEY)
        self.assertEqual(decrypt(ciphertext, self.KEY), "CATX")
        self.assertEqual(decrypt(ciphertext, self.KEY, original_length=3), "CAT")

    def test_empty_plaintext_round_trips(self) -> None:
        self.assertEqual(encrypt(" ! ", self.KEY), "")
        self.assertEqual(decrypt("", self.KEY, original_length=0), "")

    def test_rejects_invalid_ciphertext_and_original_length(self) -> None:
        with self.assertRaises(ValueError):
            decrypt("ABC", self.KEY)
        with self.assertRaises(ValueError):
            decrypt("AB", self.KEY, original_length=3)
        with self.assertRaises(ValueError):
            decrypt("A!", self.KEY)


if __name__ == "__main__":
    unittest.main()

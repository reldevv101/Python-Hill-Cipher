"""Partitioning helpers for complete, independent Hill Cipher blocks."""

from __future__ import annotations


def split_blocks(text: str, chunk_count: int) -> list[str]:
    """Split even-length A-Z text into balanced contiguous two-letter chunks."""

    if not isinstance(text, str) or len(text) % 2:
        raise ValueError("Teks yang dibagi harus berupa rangkaian blok dua huruf.")
    if any(character < "A" or character > "Z" for character in text):
        raise ValueError("Teks yang dibagi hanya boleh berisi huruf kapital A-Z.")
    if not isinstance(chunk_count, int) or isinstance(chunk_count, bool) or chunk_count <= 0:
        raise ValueError("Jumlah potongan harus berupa bilangan bulat positif.")
    block_count = len(text) // 2
    if block_count == 0:
        return []

    active_chunks = min(chunk_count, block_count)
    base_size, remainder = divmod(block_count, active_chunks)
    chunks: list[str] = []
    block_offset = 0
    for index in range(active_chunks):
        size = base_size + (1 if index < remainder else 0)
        start = block_offset * 2
        end = (block_offset + size) * 2
        chunks.append(text[start:end])
        block_offset += size
    return chunks

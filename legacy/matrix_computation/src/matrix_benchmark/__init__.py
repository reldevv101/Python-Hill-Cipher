"""Tools for benchmarking matrix computation."""

from .parallel import parallel_multiply, timed_parallel_multiply
from .sequential import multiply, timed_multiply

__all__ = ["multiply", "timed_multiply", "parallel_multiply", "timed_parallel_multiply"]

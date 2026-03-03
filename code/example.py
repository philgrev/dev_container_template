import numpy as np


def an_example_function(a: np.ndarray):
    """An example function that normalizes a numpy array."""
    return (a - np.min(a)) / (np.max(a) - np.min(a))

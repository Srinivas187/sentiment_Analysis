from typing import Any
import os

class DummyModel:
    def __init__(self, path: str):
        self._path = path

    def predict(self, sequence, verbose=0):
        # Return uniform probabilities for 3 classes
        import numpy as np
        batch_size = sequence.shape[0]
        probs = np.array([[0.33, 0.34, 0.33]] * batch_size)
        return probs


def load_model(path: str) -> Any:
    """Load a real model if present, otherwise return None.
    For development, if the path exists we return a DummyModel to avoid import errors.
    """
    if os.path.exists(path):
        return DummyModel(path)
    return None

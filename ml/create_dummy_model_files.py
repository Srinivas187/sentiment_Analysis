import pickle
from pathlib import Path
import os
import sys

# Ensure project root is in sys.path so backend imports work
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.config import MODEL_DIR

MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Create a small vocab
vocab = {'<pad>': 0, '<unk>': 1, 'this': 2, 'product': 3, 'is': 4, 'great': 5, 'bad': 6}
with open(MODEL_DIR / 'vocab.pkl', 'wb') as f:
    pickle.dump(vocab, f)

# Create minimal metadata
metadata = {'model_version': 'dummy-1', 'accuracy': 0.5}
with open(MODEL_DIR / 'model_metadata.pkl', 'wb') as f:
    pickle.dump(metadata, f)

# Create placeholder model file
with open(MODEL_DIR / 'best_model.h5', 'wb') as f:
    f.write(b'DUMMY MODEL FILE')

print('Dummy model artifacts created in', MODEL_DIR)

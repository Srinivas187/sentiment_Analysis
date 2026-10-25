import re
from backend.config import SENTIMENT_LABELS


def tokenize(text: str):
    text = text or ""
    # simple tokenizer: lowercase and split on non-word chars
    tokens = re.findall(r"\w+", text.lower())
    return tokens


def texts_to_sequences(texts, vocab, max_length=200):
    sequences = []
    for text in texts:
        tokens = tokenize(text)
        seq = [vocab.get(t, vocab.get('<unk>', 1)) for t in tokens]
        # pad/truncate
        if len(seq) < max_length:
            seq = seq + [vocab.get('<pad>', 0)] * (max_length - len(seq))
        else:
            seq = seq[:max_length]
        sequences.append(seq)
    return sequences


def int_to_label(idx: int):
    return SENTIMENT_LABELS.get(idx, 'unknown')

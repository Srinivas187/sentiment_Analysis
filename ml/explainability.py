def explain_prediction_simple(model, review_text, vocab, max_length=200):
    tokens = review_text.split() if review_text else []
    contributions = []
    for i, t in enumerate(tokens[:10]):
        contributions.append({'word': t, 'impact_score': 0.0, 'position': i})
    return {'method': 'simple', 'word_contributions': contributions}


def explain_prediction_shap(model, review_text, vocab, max_length=200):
    return {'method': 'shap', 'word_contributions': []}

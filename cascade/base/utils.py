from coolname import generate


def generate_slug(word: str) -> str:
    words = generate(3)
    return '_'.join((*words, word))

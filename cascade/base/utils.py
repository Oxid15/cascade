from coolname import generate


def generate_slug() -> str:
    words = generate(3)
    slug = "_".join(words)
    return slug

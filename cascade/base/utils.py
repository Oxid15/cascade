import os
from coolname import generate


def generate_slug() -> str:
    words = generate(3)
    slug = "_".join(words)
    return slug


def is_path(model: str) -> bool:
    # Fast check for lines
    if model.isnumeric():
        return False

    # os split will be crossplatform
    if len(os.path.normpath(model).split(os.sep)) > 1:
        return True
    else:
        return False

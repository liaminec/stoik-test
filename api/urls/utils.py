import random
import string

ALNUM = string.ascii_letters + string.digits


def short_path_generator(length: int = 7) -> str:
    if length <= 0:
        raise ValueError("length must be greater than 0")
    return "".join(random.choices(ALNUM, k=length))

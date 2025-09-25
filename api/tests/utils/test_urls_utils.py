import pytest

from urls.utils import short_path_generator


def test_short_path_generator() -> None:
    short_path = short_path_generator()
    assert len(short_path) == 7
    assert short_path.isalnum()
    short_path2 = short_path_generator()
    assert short_path != short_path2


def test_short_path_generator_diff_length() -> None:
    short_path = short_path_generator(10)
    assert len(short_path) == 10
    assert short_path.isalnum()
    short_path2 = short_path_generator(10)
    assert short_path != short_path2


def test_short_path_generator_bad_length() -> None:
    with pytest.raises(ValueError):
        short_path_generator(0)
    with pytest.raises(ValueError):
        short_path_generator(-2)

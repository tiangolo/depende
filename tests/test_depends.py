from dataclasses import FrozenInstanceError

import pytest

from depende import Depends, DependsInfo


def dependency() -> str:
    return "value"


def test_depends_returns_depends_info() -> None:
    info = Depends(dependency)

    assert info == DependsInfo(dependency=dependency, use_cache=True, scope=None)
    assert info.dependency is not None
    assert info.dependency() == "value"


def test_depends_accepts_declaration_options() -> None:
    info = Depends(dependency, use_cache=False, scope="command")

    assert info.dependency is dependency
    assert info.use_cache is False
    assert info.scope == "command"


def test_depends_info_is_frozen() -> None:
    info = Depends()

    with pytest.raises(FrozenInstanceError):
        info.use_cache = False  # type: ignore[misc]  # ty: ignore[invalid-assignment]

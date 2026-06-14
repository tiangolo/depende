from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DependsInfo:
    dependency: Callable[..., Any] | None = None
    use_cache: bool = True
    scope: str | None = None


def Depends(
    dependency: Callable[..., Any] | None = None,
    *,
    use_cache: bool = True,
    scope: str | None = None,
) -> DependsInfo:
    return DependsInfo(dependency=dependency, use_cache=use_cache, scope=scope)

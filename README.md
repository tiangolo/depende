<p align="center">
  <a href="https://depende.tiangolo.com"><img src="https://depende.tiangolo.com/img/logo-margin/logo-margin-vector.svg#only-light" alt="Depende"></a>

</p>

<p align="center">
  <em>Dependency declarations for Python frameworks and tools.</em>
</p>

<p align="center">
<a href="https://github.com/tiangolo/depende/actions?query=workflow%3ATest+event%3Apush+branch%3Amain">
    <img src="https://github.com/tiangolo/depende/actions/workflows/test.yml/badge.svg?event=push&branch=main" alt="Test">
</a>
<a href="https://github.com/tiangolo/depende/actions?query=workflow%3APublish">
    <img src="https://github.com/tiangolo/depende/actions/workflows/publish.yml/badge.svg" alt="Publish">
</a>
<a href="https://pypi.org/project/depende">
    <img src="https://img.shields.io/pypi/v/depende?color=%2334D058&label=pypi%20package" alt="Python package version">
</a>
</p>

---

**Documentation**: [https://depende.tiangolo.com](https://depende.tiangolo.com)

**Source Code**: [https://github.com/tiangolo/depende](https://github.com/tiangolo/depende)

---

`depende` provides small dependency declarations in the style of FastAPI for reuse by frameworks and tools.

## Install

```bash
uv add depende
```

Or if using pip:

```bash
pip install depende
```

## Usage

```python
from depende import Depends, DependsInfo
```

`Depends(...)` returns a frozen `DependsInfo` metadata object with:

- `dependency`: a callable dependency, or `None`
- `use_cache`: whether a framework may reuse the dependency result within its active solving context
- `scope`: an opaque framework-defined string, or `None`

The package only declares dependency metadata. It does not solve, execute, cache, inject request data, manage lifecycles, generate OpenAPI, or define framework-specific scopes.

## Example

```python
from depende import Depends
from typing import Annotated


def get_settings() -> dict[str, str]:
    return {"mode": "prod"}


SettingsDep = Annotated[dict[str, str], Depends(get_settings, scope="command")]
```

Frameworks decide what `scope` means and how dependency solving works.

## License

This project is licensed under the terms of the [MIT license](https://github.com/tiangolo/depende/blob/main/LICENSE).

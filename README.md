# depende

`depende` provides a small dependency declaration primitive extracted from FastAPI-style APIs for reuse by frameworks and tools.

```python
from depende import Depends, DependsInfo
```

`Depends(...)` returns a frozen `DependsInfo` metadata object with:

- `dependency`: a callable dependency, or `None`
- `use_cache`: whether a framework may reuse the dependency result within its active solving context
- `scope`: an opaque framework-defined string, or `None`

The package only declares dependency metadata. It does not solve, execute, cache, inject request data, manage lifecycles, generate OpenAPI, or define framework-specific scopes.

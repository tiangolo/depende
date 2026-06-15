from dataclasses import FrozenInstanceError

import pytest

from depende import (
    Depends,
    DependsInfo,
    detect_cycles,
    get_dependency_graph,
    solve_dependencies,
)


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


def test_depends_info_dependency_none_by_default() -> None:
    info = Depends()

    assert info.dependency is None
    assert info.use_cache is True
    assert info.scope is None


def test_depends_info_dependency_none_explicit() -> None:
    info = Depends(dependency=None)

    assert info.dependency is None
    assert info.use_cache is True
    assert info.scope is None


def test_depends_info_eq_equal() -> None:
    a = Depends(dependency, use_cache=False, scope="cmd")
    b = Depends(dependency, use_cache=False, scope="cmd")

    assert a == b


def test_depends_info_eq_different_dependency() -> None:
    def other() -> str:
        return "other"

    a = Depends(dependency)
    b = Depends(other)

    assert a != b


def test_depends_info_eq_different_use_cache() -> None:
    a = Depends(dependency, use_cache=True)
    b = Depends(dependency, use_cache=False)

    assert a != b


def test_depends_info_eq_different_scope() -> None:
    a = Depends(dependency, scope="a")
    b = Depends(dependency, scope="b")

    assert a != b


def test_depends_info_eq_vs_none_dependency() -> None:
    a = Depends(dependency)
    b = Depends()

    assert a != b


def test_depends_info_hash_equal_instances() -> None:
    a = Depends(dependency, use_cache=False, scope="cmd")
    b = Depends(dependency, use_cache=False, scope="cmd")

    assert hash(a) == hash(b)


def test_depends_info_hash_in_set() -> None:
    a = Depends(dependency, scope="x")
    b = Depends(dependency, scope="x")
    c = Depends(dependency, scope="y")

    s = {a, b, c}

    assert len(s) == 2


def test_depends_info_hash_in_dict() -> None:
    info = Depends(dependency, scope="x")
    d = {info: "value"}

    assert d[Depends(dependency, scope="x")] == "value"


def test_depends_info_repr() -> None:
    info = Depends(dependency, use_cache=False, scope="cmd")

    r = repr(info)

    assert "DependsInfo" in r
    assert "dependency" in r
    assert "use_cache" in r
    assert "scope" in r


def test_depends_info_repr_default() -> None:
    info = Depends()

    r = repr(info)

    assert "dependency=None" in r
    assert "use_cache=True" in r
    assert "scope=None" in r


def test_depends_with_lambda() -> None:
    info = Depends(lambda: 42)

    assert info.dependency is not None
    assert info.dependency() == 42


def test_depends_with_callable_class() -> None:
    class MyCallable:
        def __call__(self) -> int:
            return 99

    obj = MyCallable()
    info = Depends(obj)

    assert info.dependency is obj
    assert info.dependency() == 99


def test_depends_with_nested_depends() -> None:
    def inner() -> str:
        return "inner"

    def outer() -> str:
        return "outer"

    inner_info = Depends(inner)
    outer_info = Depends(outer, scope=inner_info)

    assert outer_info.dependency is outer
    assert outer_info.scope is inner_info
    assert isinstance(outer_info.scope, DependsInfo)


def test_depends_info_slots() -> None:
    info = Depends()

    assert not hasattr(info, "__dict__")


def test_depends_info_immutable_all_fields() -> None:
    info = Depends(dependency, use_cache=True, scope="s")

    with pytest.raises(FrozenInstanceError):
        info.dependency = None  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        info.use_cache = False  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        info.scope = "other"  # type: ignore[misc]


def test_depends_creates_new_instance_each_call() -> None:
    a = Depends(dependency)
    b = Depends(dependency)

    assert a is not b
    assert a == b


def test_depends_info_direct_construction() -> None:
    info = DependsInfo(dependency=dependency, use_cache=False, scope="test")

    assert info.dependency is dependency
    assert info.use_cache is False
    assert info.scope == "test"


def test_depends_all_scopes() -> None:
    for scope in [None, "", "command", "request", "app", "custom.scope"]:
        info = Depends(dependency, scope=scope)
        assert info.scope == scope


def test_depends_all_use_cache_values() -> None:
    for flag in [True, False]:
        info = Depends(dependency, use_cache=flag)
        assert info.use_cache is flag


# --- get_dependency_graph ---


def test_get_dependency_graph_single() -> None:
    info = Depends(dependency)
    graph = get_dependency_graph(info)

    assert len(graph) == 1
    assert graph[0] is info


def test_get_dependency_graph_linear_chain() -> None:
    def a() -> None:
        pass

    def b() -> None:
        pass

    def c() -> None:
        pass

    root = Depends(a, scope=Depends(b, scope=Depends(c)))
    graph = get_dependency_graph(root)

    assert len(graph) == 3
    assert graph[0] is root
    assert graph[1].dependency is b
    assert graph[2].dependency is c


def test_get_dependency_graph_diamond() -> None:
    def shared_dep() -> None:
        pass

    def a() -> None:
        pass

    def b() -> None:
        pass

    shared = Depends(shared_dep)
    a_node = Depends(a, scope=shared)
    b_node = Depends(b, scope=shared)

    graph_a = get_dependency_graph(a_node)
    graph_b = get_dependency_graph(b_node)

    assert len(graph_a) == 2
    assert len(graph_b) == 2
    assert graph_a[1] is graph_b[1]


def test_get_dependency_graph_no_nesting() -> None:
    info = Depends(dependency, scope="string_scope")
    graph = get_dependency_graph(info)

    assert len(graph) == 1


def test_get_dependency_graph_empty() -> None:
    info = Depends()
    graph = get_dependency_graph(info)

    assert len(graph) == 1
    assert graph[0].dependency is None


def test_get_dependency_graph_shared_scope() -> None:
    shared = Depends(dependency)
    a = Depends(dependency, scope=shared)
    b = Depends(dependency, scope=shared)

    graph_a = get_dependency_graph(a)
    graph_b = get_dependency_graph(b)

    assert len(graph_a) == 2
    assert len(graph_b) == 2
    assert graph_a[1] is graph_b[1]


# --- detect_cycles ---


def test_detect_cycles_no_cycle() -> None:
    def a() -> None:
        pass

    def b() -> None:
        pass

    root = Depends(a, scope=Depends(b))
    assert detect_cycles(root) is False


def test_detect_cycles_self_cycle() -> None:
    root = Depends(dependency)
    object.__setattr__(root, "scope", root)

    assert detect_cycles(root) is True


def test_detect_cycles_mutual_cycle() -> None:
    a = Depends(dependency)
    b = Depends(dependency, scope=a)
    object.__setattr__(a, "scope", b)

    assert detect_cycles(a) is True
    assert detect_cycles(b) is True


def test_detect_cycles_long_chain_no_cycle() -> None:
    nodes = [Depends(dependency) for _ in range(20)]
    for i in range(len(nodes) - 1):
        object.__setattr__(nodes[i], "scope", nodes[i + 1])

    assert detect_cycles(nodes[0]) is False


def test_detect_cycles_string_scope() -> None:
    info = Depends(dependency, scope="no_cycle_here")
    assert detect_cycles(info) is False


def test_detect_cycles_diamond_no_cycle() -> None:
    shared = Depends(dependency)
    a = Depends(dependency, scope=shared)
    b = Depends(dependency, scope=shared)

    assert detect_cycles(a) is False
    assert detect_cycles(b) is False


# --- solve_dependencies ---


def test_solve_dependencies_single() -> None:
    info = Depends(dependency)
    result = solve_dependencies(info)

    assert len(result) == 1
    assert result[0] is info


def test_solve_dependencies_linear_chain() -> None:
    def a() -> None:
        pass

    def b() -> None:
        pass

    def c() -> None:
        pass

    root = Depends(a, scope=Depends(b, scope=Depends(c)))
    result = solve_dependencies(root)

    assert len(result) == 3
    result_deps = [n.dependency for n in result]
    assert result_deps.index(c) < result_deps.index(b)
    assert result_deps.index(b) < result_deps.index(a)


def test_solve_dependencies_independent() -> None:
    a = Depends(dependency, scope="x")
    root = Depends(dependency, scope=a)

    result = solve_dependencies(root)

    assert len(result) == 2
    result_deps = [n.dependency for n in result]
    assert dependency in result_deps


def test_solve_dependencies_diamond() -> None:
    def shared_dep() -> None:
        pass

    def a() -> None:
        pass

    def b() -> None:
        pass

    shared = Depends(shared_dep)
    a_node = Depends(a, scope=shared)
    b_node = Depends(b, scope=shared)

    result_a = solve_dependencies(a_node)
    result_b = solve_dependencies(b_node)

    assert len(result_a) == 2
    assert len(result_b) == 2
    result_a_deps = [n.dependency for n in result_a]
    result_b_deps = [n.dependency for n in result_b]
    assert result_a_deps.index(shared_dep) < result_a_deps.index(a)
    assert result_b_deps.index(shared_dep) < result_b_deps.index(b)


def test_solve_dependencies_returns_list() -> None:
    info = Depends(dependency)
    result = solve_dependencies(info)

    assert isinstance(result, list)
    assert all(isinstance(n, DependsInfo) for n in result)


def test_solve_dependencies_dependency_first() -> None:
    def a() -> None:
        pass

    def b() -> None:
        pass

    root = Depends(a, scope=Depends(b))
    result = solve_dependencies(root)

    assert result[0].dependency is b
    result_deps = [n.dependency for n in result]
    assert result_deps.index(b) < result_deps.index(a)


def test_solve_dependencies_all_present() -> None:
    def a() -> None:
        pass

    def b() -> None:
        pass

    def c() -> None:
        pass

    root = Depends(a, scope=Depends(b, scope=Depends(c)))
    result = solve_dependencies(root)
    result_set = {id(n) for n in result}

    assert id(root) in result_set
    assert len(result) == len(set(result))


# --- __version__ ---


def test_version_exists() -> None:
    import depende

    assert hasattr(depende, "__version__")
    assert isinstance(depende.__version__, str)


def test_version_is_not_empty() -> None:
    import depende

    assert len(depende.__version__) > 0

from __future__ import annotations

import re
import typing
from typing import Any, Callable, TypeVar

import numpy as np
import pytest

import matplotlib as mpl
from matplotlib import _api


if typing.TYPE_CHECKING:
    from typing_extensions import Self

T = TypeVar('T')


@pytest.mark.parametrize('target,test_shape',
                         [((None, ), (1, 3)),
                          ((None, 3), (1,)),
                          ((None, 3), (1, 2)),
                          ((1, 5), (1, 9)),
                          ((None, 2, None), (1, 3, 1))
                          ])
def test_check_shape(target: tuple[int | None, ...],
                     test_shape: tuple[int, ...]) -> None:
    error_pattern = (f"^'aardvark' must be {len(target)}D.*" +
                     re.escape(f'has shape {test_shape}'))
    data = np.zeros(test_shape)
    with pytest.raises(ValueError, match=error_pattern):
        _api.check_shape(target, aardvark=data)


def test_classproperty_deprecation() -> None:
    class A:
        @_api.deprecated("0.0.0")
        @_api.classproperty
        def f(cls: Self) -> None:
            pass
    with pytest.warns(mpl.MatplotlibDeprecationWarning):
        A.f
    with pytest.warns(mpl.MatplotlibDeprecationWarning):
        a = A()
        a.f


def test_deprecate_privatize_attribute() -> None:
    class C:
        def __init__(self) -> None: self._attr = 1
        def _meth(self, arg: T) -> T: return arg
        attr: int = _api.deprecate_privatize_attribute("0.0")
        meth: Callable = _api.deprecate_privatize_attribute("0.0")

    c = C()
    with pytest.warns(mpl.MatplotlibDeprecationWarning):
        assert c.attr == 1
    with pytest.warns(mpl.MatplotlibDeprecationWarning):
        c.attr = 2
    with pytest.warns(mpl.MatplotlibDeprecationWarning):
        assert c.attr == 2
    with pytest.warns(mpl.MatplotlibDeprecationWarning):
        assert c.meth(42) == 42


def test_delete_parameter() -> None:
    @_api.delete_parameter("3.0", "foo")
    def func1(foo: Any = None) -> None:
        pass

    @_api.delete_parameter("3.0", "foo")
    def func2(**kwargs: Any) -> None:
        pass

    for func in [func1, func2]:  # type: ignore[list-item]
        func()  # No warning.
        with pytest.warns(mpl.MatplotlibDeprecationWarning):
            func(foo="bar")

    def pyplot_wrapper(foo: Any = _api.deprecation._deprecated_parameter) -> None:
        func1(foo)

    pyplot_wrapper()  # No warning.
    with pytest.warns(mpl.MatplotlibDeprecationWarning):
        func(foo="bar")


def test_make_keyword_only() -> None:
    @_api.make_keyword_only("3.0", "arg")
    def func(pre: Any, arg: Any, post: Any = None) -> None:
        pass

    func(1, arg=2)  # Check that no warning is emitted.

    with pytest.warns(mpl.MatplotlibDeprecationWarning):
        func(1, 2)
    with pytest.warns(mpl.MatplotlibDeprecationWarning):
        func(1, 2, 3)


def test_deprecation_alternative() -> None:
    alternative = "`.f1`, `f2`, `f3(x) <.f3>` or `f4(x)<f4>`"
    @_api.deprecated("1", alternative=alternative)
    def f() -> None:
        pass
    if f.__doc__ is None:
        pytest.skip('Documentation is disabled')
    assert alternative in f.__doc__


def test_empty_check_in_list() -> None:
    with pytest.raises(TypeError, match="No argument to check!"):
        _api.check_in_list(["a"])

from typing import Callable, Iterable, TypeVar

T = TypeVar("T")


def chain(*functions: Callable[[T], T]) -> Callable[[T], T]:
    def returned_function(var: T) -> T:
        for func in functions:
            var = func(var)
        return var

    return returned_function

from typing import Any, Callable, List, TypeVar

T = TypeVar("T")


def chain(*functions: Callable[[T], T]) -> Callable[[T], T]:
    """Create a chained function

    Returns:
        Callable[[T], T]: Iterable of callables that accept the same arguments
    """

    def returned_function(var: T) -> T:
        for func in functions:
            var = func(var)
        return var

    return returned_function


def argument_list_type(type_: T):
    """Custom function to cast request parser list argments

    Args:
        type_ (T): Basic type to try and cast list elements
    """

    def checker(val: Any) -> List[T]:
        if not isinstance(val, list) and False in [
            isinstance(val_, type_) for val_ in val
        ]:
            raise TypeError
        return val

    return checker

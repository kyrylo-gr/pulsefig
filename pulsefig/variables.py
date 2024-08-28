import types
from typing import Callable, Optional


def get_value(obj):
    return getattr(obj, "value", obj)


def hash_lambda(f):
    if not isinstance(f, types.LambdaType):
        return hash(f)

    # Get the bytecode of the lambda function
    bytecode = f.__code__.co_code
    # Get the constants used in the lambda function
    constants = f.__code__.co_consts
    # Get the names of variables used
    varnames = f.__code__.co_varnames

    return hash(
        bytecode + bytes(str(constants), "utf-8") + bytes(str(varnames), "utf-8")
    )


class AttrLink:
    def __init__(self, obj, attr_name):
        self.obj = obj
        self.attr_name = attr_name

    @property
    def value(self):
        value = getattr(self.obj, self.attr_name, None)
        return value

    def __repr__(self) -> str:
        return f"Link to {self.obj}.{self.attr_name}"

    def __hash__(self) -> int:
        return hash(hash(self.obj) + hash(self.attr_name))


class FloatProxy(float):
    def __new__(cls, link: AttrLink, post_func: Optional[Callable] = None):
        return super().__new__(cls, 0)

    def __init__(self, link: AttrLink, post_func: Optional[Callable] = None):
        self.link = link
        self.post_func = post_func if post_func is not None else (lambda v: v)

    @property
    def value(self):
        value = self.link.value
        if value is None:
            return 0.0
        return self.post_func(value)

    def __float__(self):
        return float(self.value)

    def __add__(self, other):
        value = self.link.value
        if value is not None:
            return float(self.post_func(value)) + other
        return self.__class__(self.link, lambda v: self.post_func(v) + float(other))

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        value = self.link.value
        if value is not None:
            return float(self.post_func(value)) - other
        return self.__class__(self.link, lambda v: self.post_func(v) - float(other))

    def __rsub__(self, other):
        value = self.link.value
        if value is not None:
            return other - float(self.post_func(value))
        return self.__class__(self.link, lambda v: other - self.post_func(v))

    def __mul__(self, other):
        value = self.link.value
        if value is not None:
            return float(self.post_func(value)) * other
        return self.__class__(self.link, lambda v: self.post_func(v) * float(other))

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        value = self.link.value
        if value is not None:
            return float(self.post_func(value)) / other
        return self.__class__(self.link, lambda v: self.post_func(v) / float(other))

    def __repr__(self) -> str:
        return f"FloatProxy {self.link} = {self.value}"

    def __eq__(self, other):  # type: ignore
        value = self.link.value
        other_value = get_value(other)
        # print("__eq__", value, other)
        if value is not None and other is not None:
            return value == other_value
        return self.__class__(self.link, lambda v: self.post_func(v) == other)

    def __ne__(self, other):  # type: ignore
        value = self.link.value
        other_value = get_value(other)
        if value is not None and other is not None:
            return value != other_value
        return self.__class__(self.link, lambda v: self.post_func(v) != other)

    def __lt__(self, other):  # type: ignore
        value = self.link.value
        other_value = get_value(other)
        if value is not None and other is not None:
            return value < other_value
        return self.__class__(self.link, lambda v: self.post_func(v) < other)

    def __gt__(self, other):  # type: ignore
        value = self.link.value
        other_value = get_value(other)
        if value is not None and other is not None:
            return value > other_value
        return self.__class__(self.link, lambda v: self.post_func(v) > other)

    def __le__(self, other):  # type: ignore
        value = self.link.value
        other_value = get_value(other)
        if value is not None and other is not None:
            return value <= other_value
        return self.__class__(self.link, lambda v: self.post_func(v) <= other)

    def __ge__(self, other):  # type: ignore
        value = self.link.value
        other_value = get_value(other)
        if value is not None and other is not None:
            return value >= other_value
        return self.__class__(self.link, lambda v: self.post_func(v) >= other)

    def __hash__(self) -> int:
        return hash(hash(self.link) + hash_lambda(self.post_func))


class UnsetParameter:
    def __set_name__(self, owner, name):
        self.private_name = "_" + name  # pylint: disable=attribute-defined-outside-init

    def __get__(self, instance, owner):
        value = getattr(instance, self.private_name, None)
        if value is None:
            return FloatProxy(AttrLink(instance, self.private_name))
        return value

    def __set__(self, instance, value):
        setattr(instance, self.private_name, value)

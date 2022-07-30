import string
from typing import Any, Literal, Mapping, Sequence, Set, Type

from disnake.utils import MISSING

__all__ = ("DisnakeFormatter",)


class DisnakeFormatter(string.Formatter):
    """Allows using formatting without allowing keys that aren't whitelisted.

    By default, this allows all builtin types."""

    def __init__(self, allowed_mapping: Mapping[Type, Set[str]] = MISSING):
        self.allowed_mapping = allowed_mapping

    def vformat(self, format_string: str, args: Sequence[Any], kwargs: Mapping[str, Any]) -> str:
        if args:
            raise ValueError("args are not supported by this formatter.")
        return super().vformat(format_string, args, kwargs)

    def convert_field(self, value: Any, conversion: str) -> Any:
        if conversion and conversion != "s":
            raise ValueError("conversion must be 's'")
        return super().convert_field(value, "s")

    def _validate_with_custom_mapping(self, qualname: str, obj: Any, parent: str) -> Literal[True]:

        childname = qualname.split(".", 1)[1]
        single_child_name = qualname.split(".")[1]
        for kind, values in self.allowed_mapping.items():
            if not isinstance(obj, kind):
                continue

            if single_child_name not in values:
                continue

            # if we need to keep going
            if "." in childname:
                child_attr = getattr(obj, childname.split(".", 1)[0])
                self._validate_with_custom_mapping(childname, child_attr, parent=parent)
            break
        else:
            raise TypeError(f"cannot use {qualname} on {parent}")
        return True

    def _validate_allowed_attribute(self, qualname: str, obj: Any, parent: str) -> Literal[True]:
        def get_top_module(obj: Any):
            try:
                return type(obj).__module__.split(".", 1)[0]
            except AttributeError:
                return None

        if "." not in qualname:
            return True
        children = qualname.split(".")[1:]
        for childname in children:
            module = get_top_module(obj)
            if module and module == "disnake":
                attr = getattr(obj, childname)
                if childname.startswith("_"):
                    raise TypeError(f"cannot access private attribute {qualname} on {parent}")
                module = get_top_module(attr)
                if module != "disnake" and type(attr) not in (set, int, float, str):
                    raise TypeError(f"cannot use attribute {qualname} on {parent}")

        return True

    def get_field(self, field_name: str, args: Sequence[Any], kwargs: Mapping[str, Any]) -> Any:
        obj, used_key = super().get_field(field_name, args, kwargs)
        attr = field_name[len(used_key) :].lstrip(".")

        if attr and not attr.isspace():
            if self.allowed_mapping is MISSING:
                self._validate_allowed_attribute(field_name, kwargs[used_key], parent=used_key)
            else:
                self._validate_with_custom_mapping(field_name, kwargs[used_key], parent=used_key)

        return obj, used_key

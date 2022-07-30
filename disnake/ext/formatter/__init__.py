import string
from typing import Any, Literal, Mapping, Sequence, Set, Type

from disnake.utils import MISSING

import disnake

__all__ = ("DisnakeFormatter",)


class BlockedAttributeError(AttributeError):
    """A subclass of AttributeError which is raised when an attribute exists but access is blocked."""


class DisnakeFormatter(string.Formatter):
    """Allows using formatting without allowing keys that aren't whitelisted.

    By default, this allows all builtin types."""

    def __init__(
        self,
        allowed_mapping: Mapping[Type, Set[str]] = MISSING,
        *,
        suppress_blocked_errors: bool = False,
    ):
        if allowed_mapping is MISSING:
            self.allowed_mapping = {
                disnake.abc.GuildChannel: {
                    "category",
                    "created_at",
                    "guild",
                    "id",
                    "jump_url",
                    "mention",
                    "name",
                    "type",
                },
                disnake.Guild: {
                    "approximate_member_count",
                    "approximate_presence_count",
                    "created_at",
                    "description",
                    "id",
                    "name",
                    "owner_id",
                    "preferred_locale",
                    "premium_progress_bar_enabled",
                    "premium_subscription_count",
                    "premium_tier",
                    "rules_channel",
                    "vanity_url_code",
                },
                disnake.Invite: {
                    "approximate_member_count",
                    "approximate_presence_count",
                    "channel",
                    "code",
                    "created_at",
                    "expires_at",
                    "guild",
                    "inviter",
                    "max_uses",
                    "target_type",
                    "target_user",
                    "uses",
                },
                disnake.Member: {
                    "bot",
                    "created_at",
                    "discriminator",
                    "display_name",
                    "guild",
                    "id",
                    "joined_at",
                    "mention",
                    "name",
                    "nick",
                    "pending",
                    "premium_since",
                    "system",
                },
                disnake.Message: {
                    "author",
                    "channel",
                    "content",
                    "created_at",
                    "guild",
                    "id",
                },
                disnake.User: {
                    "bot",
                    "created_at",
                    "discriminator",
                    "id",
                    "mention",
                    "name",
                    "system",
                },
                disnake.Role: {
                    "created_at",
                    "guild",
                    "hoist",
                    "id",
                    "managed",
                    "mention",
                    "mentionable",
                    "name",
                    "position",
                },
            }
        elif allowed_mapping is None:
            self.allowed_mapping = {}
        else:
            self.allowed_mapping = allowed_mapping
        self.suppress_blocked_errors = suppress_blocked_errors

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
            raise BlockedAttributeError(f"cannot use {qualname} on {parent}")
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
                    raise BlockedAttributeError(
                        f"cannot access private attribute {qualname} on {parent}"
                    )
                module = get_top_module(attr)
                if module != "disnake" and type(attr) not in (set, int, float, str):
                    raise BlockedAttributeError(f"cannot use attribute {qualname} on {parent}")

        return True

    def get_field(self, field_name: str, args: Sequence[Any], kwargs: Mapping[str, Any]) -> Any:
        obj, used_key = super().get_field(field_name, args, kwargs)
        attr = field_name[len(used_key) :].lstrip(".")

        try:
            if attr and not attr.isspace():
                if not self.allowed_mapping:
                    self._validate_allowed_attribute(field_name, kwargs[used_key], parent=used_key)
                else:
                    self._validate_with_custom_mapping(
                        field_name, kwargs[used_key], parent=used_key
                    )

        except BlockedAttributeError:
            if not self.suppress_blocked_errors:
                raise

            # otherwise return the objects so we silently error
            return "{" + field_name + "}", ""

        return obj, used_key

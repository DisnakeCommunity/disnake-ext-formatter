# disnake.ext.formatter

`disnake.ext.formatter` is a module with a single class: a [`string.Formatter`](https://docs.python.org/3/library/string.html#string.Formatter '(in python v3.10)') subclass.

This class, aptly named `DisnakeFormatter`, has special handling for disnake objects, in order to hide attributes that shouldn't be otherwise exposed.


> This project is currently in an **alpha** state and should **not** be used in production code without understanding the risks.

### Why is this needed?

With simple string format, user provided strings can easily give away your token if they know the attributes. There are some ways to get around these, but rely on hacks and validating the strings ahead of time, or scanning the output for known secrets, but this cannot catch all cases.

For example, the code below would reveal the bot token to the user.

```python
USER_PROVIDED_STRING = "Welcome to {guild.name}, {member!s}! Also this bot's token is {member._state.http.token}!"


@client.event
async def on_member_join(member: disnake.Member):
    # process getting the guild and other config
    result = USER_PROVIDED_STRING.format(member=member)
    await member.send(result)
```

> This example has been shortened for brevity. The typical usecase would be when there a configurable bot message that a user can change the content, and has access to a user/channel/guild/role object.

However, we require that none of the attributes that are attempted to access are private attributes, which mean this attack is not possible when using the  `DisnakeFormatter` class correctly.

Future plans include having a hardcoded list of attributes which can be accessed on objects, the option to set that list to a desired mapping, and limiting attributes to specific types, to name but a few.

### Examples

Because `DisnakeFormatter` is a subclass of [`string.Formatter`](https://docs.python.org/3/library/string.html#string.Formatter '(in python v3.10)'), the behaviour is the same. However, this is *not* the same as using [`str.format`](https://docs.python.org/3/library/stdtypes.html#str.format '(in python v3.10)').
To use `DisnakeFormatter`, an instance of the class is required, of which there are no special arguments. From there, all that is necessary to do is use the `format` method, which follows the same behavior as [`string.Formatter.format()`](https://docs.python.org/3/library/string.html#string.Formatter.format '(in python v3.10)').

```python
from disnake.ext.formatter import DisnakeFormatter

USER_PROVIDED_STRING = "Welcome to {guild.name}, {member!s}! Also this bot's token is {member._state.http.token}!"


@client.event
async def on_member_join(member: disnake.Member):
    # process getting the guild and other config
    formatter = DisnakeFormatter()
    result = formatter.format(USER_PROVIDED_STRING, member=member)
    await member.send(result)
```

Instead of exposing the token, this will helpfully raise an error mentioning the attribute cannot be accessed on `member`.

----

<br>
<p align="center">
    <a href="https://docs.disnake.dev/">Documentation</a>
    ⁕
    <a href="https://guide.disnake.dev/">Guide</a>
    ⁕
    <a href="https://discord.gg/disnake">Discord Server</a>

</p>
<br>

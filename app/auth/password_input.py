
"""Secure password input with visible asterisk masking."""

import os
import sys
from getpass import getpass


def ask_password(prompt="Password: "):
    """Read a password while displaying * for each character."""

    if os.name != "nt":
        return getpass(prompt)

    import msvcrt

    password = []

    print(prompt, end="", flush=True)

    while True:
        key = msvcrt.getwch()

        if key in ("\r", "\n"):
            print()
            return "".join(password)

        elif key in ("\b", "\x7f"):
            if password:
                password.pop()
                sys.stdout.write("\b \b")
                sys.stdout.flush()

        elif key in ("\x00", "\xe0"):
            msvcrt.getwch()

        elif key == "\x03":
            raise KeyboardInterrupt

        elif key.isprintable():
            password.append(key)
            sys.stdout.write("*")
            sys.stdout.flush()

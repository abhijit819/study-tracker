import os
import sys


def get_key(prompt="Choose an option: "):
    # Blocking single-key input; no polling loop.
    print(prompt, end="", flush=True)
    if not sys.stdin.isatty():
        value = input()
        return value[:1].upper() if value else ""

    if os.name == "nt":
        import msvcrt
        while True:
            key = msvcrt.getwch()
            if key in ("\x00", "\xe0"):
                msvcrt.getwch()
                continue
            print(key)
            return key.upper()

    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    print(key)
    return key.upper()

import os
from .hiccup import run


def main():
    if os.geteuid() == 0:
        print("please don't run this as root :(")
        exit(1)
    try:
        run()
        print("done!")
    except Exception as e:
        print(repr(e))
        exit(2)

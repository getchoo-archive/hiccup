#!/usr/bin/env python3
import argparse
import os
from .helpers import DistroHelper, DistroNotSupportedError, get_distro_id


def run():
    CONFIG_FILE = os.path.join(os.environ["XDG_CONFIG_HOME"], "hiccup/config.json")
    OS_RELEASE_PATH = "/etc/os-release"

    current_distro = str()
    try:
        current_distro = get_distro_id(OS_RELEASE_PATH)
    except DistroNotSupportedError:
        pass
    distro = DistroHelper(current_distro, CONFIG_FILE)

    parser = argparse.ArgumentParser(
        description="a python script to help keep you up to date"
    )
    parser.add_argument(
        "--cleanonly",
        "-c",
        action="store_true",
        default=False,
        dest="clean_only",
        help="cleanup unneeded dependencies",
    )
    parser.add_argument(
        "--systemonly",
        "-s",
        action="store_true",
        default=False,
        dest="system_only",
        help="only update through the system's package manager",
    )
    args = parser.parse_args()

    if args.clean_only:
        return distro.cleanup_system()
    if args.system_only:
        return distro.update_system()

    return distro.update_all()

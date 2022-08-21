#!/usr/bin/env python3
import argparse
import json
import subprocess  # nosec:b404
import os

CONFIG_FILE = os.path.join(os.environ["XDG_CONFIG_HOME"], "hiccup/config.json")
OS_RELEASE_PATH = "/etc/os-release"


class DistroNotSupportedError(Exception):
    def __init__(self, name):
        self.message = "{} isn't supported yet".format(name)
        super().__init__(self.message)


class Distro:
    def __init__(self, id: str, config_file: os.path):
        try:
            # read and store commands from config file
            with open(config_file) as file:
                data = json.load(file)
                self.__system_update_cmds = data["system_update_cmds"]
                self.__extra_cmds = data["extra_cmds"]
                self.__clean_cmds = data["clean_cmds"]
                self.__shell_plugin_cmds = data["shell_plugin_cmds"]
                self.__other_cmds = data["other_cmds"]
        except OSError:
            raise OSError("no config file found!")
        except json.JSONDecodeError:
            raise json.JSONDecodeError("unable to parse json")

        self.id = id

        # get commands specific to current distro
        if self.is_supported():
            self.update_cmd = self.get_update_cmd()
            if self.has_clean_cmd():
                self.clean_cmd = self.get_clean_cmd()
            if self.has_extra_cmd():
                self.extra_cmd = self.get_extra_cmd()
        else:
            raise DistroNotSupportedError(self.id)

    def __get_cmd(self, dct: dict):
        return dct[self.id]

    # wrapper for subprocess.run that allows for easy privlage escalation,
    # silencing, and variable shells
    def __sys_cmd(self, cmd: str, shell="bash", silent=False, sudo=False):
        args = list()
        if silent:
            cmd += " > /dev/null 2>&1"
        if sudo:
            args += ["/usr/bin/sudo"]

        args += [shell, "-c", cmd]

        return subprocess.run(args, check=True)  # nosec:B603

    # iterate through dict of commands, optionally allow for keys to
    # determine the shell the command is run though
    def __run_items(self, msg: str, dct: dict, name_as_shell=False):
        shell = "bash"
        for name, cmd in dct.items():
            print(msg.format(name))

            if name_as_shell:
                shell = name
            self.__sys_cmd(cmd, shell=shell, silent=True)  # nosec:B604

    def is_supported(self):
        return self.id in self.__system_update_cmds

    def has_clean_cmd(self):
        return self.id in self.__clean_cmds

    def has_extra_cmd(self):
        return self.id in self.__extra_cmds

    def get_update_cmd(self):
        return self.__get_cmd(self.__system_update_cmds)

    def get_extra_cmd(self):
        return self.__get_cmd(self.__extra_cmds)

    def get_clean_cmd(self):
        return self.__get_cmd(self.__clean_cmds)

    def update_system(self):
        self.__sys_cmd(self.update_cmd, sudo=True)
        if self.has_extra_cmd():
            self.__sys_cmd(self.extra_cmd)

    def cleanup_system(self):
        if self.has_clean_cmd():
            print("cleaning up system...")
            return self.__sys_cmd(self.clean_cmd, sudo=True)
        print("no cleanup command found for {}".format(self.id))

    def update_shell_plugins(self):
        msg = "updating {} plugins..."
        return self.__run_items(msg, self.__shell_plugin_cmds, name_as_shell=True)

    def update_other(self):
        msg = "updating {}..."
        return self.__run_items(msg, self.__other_cmds)

    def update_all(self):
        self.update_system()
        self.update_shell_plugins()
        self.update_other()
        self.cleanup_system()


# reads id from an os-release file
def get_distro_id(filename: os.path):
    with open(filename) as file:
        for line in file.readlines():
            k, v = line.strip().split("=")
            if k == "ID":
                return v


def run():
    try:
        current_distro = get_distro_id(OS_RELEASE_PATH)
    except DistroNotSupportedError:
        pass
    distro = Distro(current_distro, CONFIG_FILE)

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


if __name__ == "__main__":
    if os.geteuid() == 0:
        print("please don't run this as root :(")
        exit(1)
    try:
        run()
        print("done!")
    except Exception as e:
        print(repr(e))
        exit(2)

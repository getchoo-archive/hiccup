import json
import subprocess  # nosec:b404


class DistroNotSupportedError(Exception):
    def __init__(self, name):
        self.message = "{} isn't supported yet".format(name)
        super().__init__(self.message)


class DistroHelper:
    def __init__(self, id: str, config_file: str):
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
            pass

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
def get_distro_id(filename: str):
    with open(filename) as file:
        for line in file.readlines():
            k, v = line.strip().split("=")
            if k == "ID":
                return v
    return ""

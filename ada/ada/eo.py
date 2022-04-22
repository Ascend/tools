# Environment Operator
import os
import logging
from . import local_machine
from . import shell_printer


class ExecutionFailedException(Exception):
    pass


class AscendShell:
    @staticmethod
    def create_local():
        shell = AscendShell()
        shell._handle = local_machine.LocalMachine()
        return shell

    def __init__(self):
        self._encoding = 'utf-8'
        self._handle = None

    def file_exists(self, file_path):
        return os.path.isfile(file_path)

    def exec_command(self, cmd):
        return self._handle.exec_command(cmd)

    def install(self, package_path, install_path=None):
        if not self.file_exists(package_path):
            logging.error("The install package {} does not exists".format(package_path))
            raise FileNotFoundError("The file {} does not exists".format(package_path))
        self.exec_command("chmod +x {}".format(package_path))
        if package_path.startswith('/'):
            cmd = "{} --full --quiet".format(package_path)
        else:
            cmd = "./{} --full --quiet".format(package_path)
        if install_path is not None:
            cmd = "{} --install-path={}".format(cmd, install_path)
        else:
            install_path = "default location"
        with shell_printer.DotPrinter("Begin to install package {} to {}".format(package_path, install_path)):
            _, out, _ = self.exec_command(cmd)
        ret: str = out.read().decode(self._encoding)
        logging.debug("Install {}, echo {}".format(package_path, ret))
        for line in ret.splitlines():
            if line.find(" install success") > 0:
                print("Install package {} success({})".format(package_path, line))
                return
            if line.find(" installed successfully") > 0:
                print("Install package {} success({})".format(package_path, line))
                return
        raise ExecutionFailedException("Failed to install package {}\n{}".format(package_path, ret))

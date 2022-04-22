import subprocess


class LocalChannel:
    def __init__(self, ret):
        self._ret = ret

    def read(self):
        return self._ret


class LocalMachine:
    def exec_command(self, cmd: str):
        ret = subprocess.run(cmd.split(), capture_output=True)
        return None, LocalChannel(ret.stdout), LocalChannel(ret.stderr)

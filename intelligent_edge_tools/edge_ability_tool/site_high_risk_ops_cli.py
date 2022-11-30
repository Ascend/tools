# coding: utf-8
import json
import logging
import os
import sys

from edge_om.src.utils.high_risk.high_risk_op_policy import SiteHighRiskOp, HighRiskConfig
from glib.utils.high_risk_op_policy import Cmd
from glib.utils.high_risk_op_policy import CmdDisableAllOpt
from glib.utils.high_risk_op_policy import HighRiskOpPolicyCli
from glib.utils.high_risk_op_policy import SwitchVal

logging.basicConfig(format='%(message)s', level=logging.INFO)


class SiteCli(HighRiskOpPolicyCli):
    """
    SITE cli类
    """

    pass


SITE_CMDS_CONF = {
    "description": "config site high risk operations policy.",
    "prog": "site_ability_policy.sh",
    "sub_cmds": [
        {
            "cmd": Cmd.DISABLE_ALL.value,
            "help": "disable all ops.",
            "opts": [
                {
                    "name": CmdDisableAllOpt.ON.value,
                    "default": SwitchVal.OFF,
                    "help": "disable all high risk operations.",
                }
            ]
        },
        {
            "cmd": Cmd.ALLOW.value,
            "help": "allow ops.",
            "opts": [
                {
                    "name": SiteHighRiskOp.CREATE_CONTAINER.value,
                    "default": SwitchVal.OFF,
                    "help": "to enable create_container.",
                },
                {
                    "name": SiteHighRiskOp.DOWNLOAD_MODEL_FILE.value,
                    "default": SwitchVal.OFF,
                    "help": "to enable download_model_file operations for creating container",
                },
            ],
        }
    ]
}


class HelpException(Exception):
    pass


def check_param(parser: HighRiskOpPolicyCli):
    """
    命令行参数预检查
    :param parser:
    :return: 为True表示参数校验通过, False仅表示help帮助命令输入正确，异常表示命令参数输错
    """
    help_opts = ('-h', '--help')
    arg_num = len(sys.argv)
    # 总命令带help或不带help
    if arg_num == 1:
        parser.print_help()
        raise HelpException()

    # 参数个数为2且第二个参数在('disable_all', 'allow')内
    if arg_num == 2 and (sys.argv[1] in Cmd.values()):
        cmd = sys.argv[1]
        if parser.print_help(cmd):
            raise HelpException()

    # 参数个数为2且第二个参数不在('-h', '--help', 'disable_all', 'allow')内
    if arg_num >= 2 and (sys.argv[1] not in Cmd.values() and sys.argv[1] not in help_opts):
        parser.print_help()
        raise HelpException()

    # 参数个数为2且第二个参数在('-h', '--help')内
    if arg_num == 2 and (sys.argv[1] in help_opts):
        if parser.print_help():
            return False

    # 参数个数为3, 第二个参数在('disable_all', 'allow')内, 第三个参数在('-h', '--help')内
    if arg_num == 3 and (sys.argv[1] in Cmd.values() and sys.argv[2] in help_opts):
        cmd = sys.argv[1]
        if parser.print_help(cmd):
            return False

    return True


def cli_set_config(config_file):
    """
    从命令行读取，写入配置文件
    :return:
    """
    cli = SiteCli(SITE_CMDS_CONF, SiteHighRiskOp)
    cli.gen_cli_parser()
    if not check_param(cli):
        # 返回结果为4, 仅表示help帮助命令输入正确
        return 4

    dto = cli.parse_args()
    config_data = dto.dump_to_json()

    # 适配当2.0.4.6和3.0.RC3删除网管注册高危配置net_config后，执行disable_all，再升级到3.0.RC2出现net_config找不到的场景
    if config_data["disable_all"]:
        config_data["disable_all"] = False
    config_data["allow"]["net_config"] = True

    json_str = json.dumps(config_data, indent=2)
    with os.fdopen(os.open(config_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644), "w") as f:
        f.write(json_str)

    config_info_str = json.dumps((dto.dump_to_json()), indent=2)

    logging.info("Write to config file success")
    logging.info(config_info_str)
    logging.info("Warning: You also need to restart AtlasEdge for the configuration to take effect.\n")
    return 0


def main():
    try:
        ret_code = cli_set_config(HighRiskConfig().config_file)
    except HelpException:
        ret_code = 1
    except Exception as e:
        ret_code = 2
        logging.info(f"run cmd failed, {e}")
    except SystemExit:
        ret_code = 3

    return ret_code


if __name__ == "__main__":
    exit(main())

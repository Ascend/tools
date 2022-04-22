import argparse
import sys
import logging
import os
from collections import OrderedDict
from ada import cip
from ada import eo
from ada import VERSION as ada_version


NAMES_TO_TYPE = {
    'compiler': cip.PackageType.COMPILER_CANN,
    'runtime': cip.PackageType.RUNTIME_CANN,
    'opp': cip.PackageType.OPP_CANN,
    'plugin': cip.PackageType.FWKPLUGIN_CANN,
    'toolkit': cip.PackageType.TOOLKIT_CANN,

    'opp-ot': cip.PackageType.OPP_ONETRACK,
    'atc': cip.PackageType.ATC_ONETRACK,
    'acllib': cip.PackageType.ACLLIB_ONETRACK,
    'fwkacllib': cip.PackageType.FWKACLLIB_ONETRACK,
    'toolkit-ot': cip.PackageType.TOOLKIT_ONETRACK,
    'plugin-ot': cip.PackageType.TFPLUGIN_ONETRACK
}

NAME_ALIAS_TO_NAME = {
    'c': 'compiler',
    'r': 'runtime',
    'o': 'opp',
    'p': 'plugin'
}


def generate_package_names_help():
    global NAMES_TO_TYPE, NAME_ALIAS_TO_NAME
    names = OrderedDict()
    for name_alias, name in NAME_ALIAS_TO_NAME.items():
        names[name] = "{}({})".format(name, name_alias)
    for name in NAMES_TO_TYPE:
        if name in names:
            continue
        names[name] = name
    return ','.join(names.values())


def parse_args(str_args):
    parser = argparse.ArgumentParser(prog='ada', description="Ascend Debugging Assistant")
    parser.add_argument('-w', '--wait', action='store_true', default=True)
    parser.add_argument('-n', '--newest', help='Download one or more the newest packages, specify packages by name, '
                                               'supported package names: {}'.format(generate_package_names_help()))
    parser.add_argument('-c', '--compile', help='Download one or more self-compiled packages')
    parser.add_argument('-i', '--install', action='store_true', default=False, help='Install packages downloaded')
    parser.add_argument('-d', '--directory', default='./', help='Temporary packages save directory')
    parser.add_argument('--install-path', default=None, help='Specify the path where to install, see help info in .run')
    parser.add_argument('-v', '--version', action='store_true', help='Print the version of ada')

    return parser.parse_args(str_args)


def parse_package_types(package_types):
    packages = set()
    for p_type in package_types.split(','):
        p_type = p_type.strip()
        packages.add(p_type)
    return packages


def convert_package_types(package_names):
    global NAMES_TO_TYPE
    packages = set()
    for package in package_names:
        if package in NAME_ALIAS_TO_NAME:
            package = NAME_ALIAS_TO_NAME[package]
        if package not in NAMES_TO_TYPE:
            logging.error(
                "Unexpect package type {}, only accept package types: {}".format(package, NAMES_TO_TYPE.keys()))
            raise Exception("Unexpected package type")
        packages.add(NAMES_TO_TYPE[package])
    return packages


def check_packages(args):
    newest_packages = set()
    compile_packages = set()
    if args.newest is not None:
        newest_packages = parse_package_types(args.newest)
    if args.compile is not None:
        compile_args = args.compile.split(',')
        if len(compile_args) <= 1:
            logging.error("The '-c' option should in format: <compile-name>,package_types[,package_types].")
            raise Exception("Invalid argument '-c'")
        compile_packages = parse_package_types(','.join(compile_args[1:]))

    duplicated_packages = newest_packages & compile_packages
    if len(duplicated_packages) > 0:
        logging.error("Same package types specified by -n and -c: {}".format(duplicated_packages))
        raise Exception("Same package types specified by -n and -c.")

    return convert_package_types(newest_packages), convert_package_types(compile_packages)


def download(args):
    newest_packages, compile_packages = check_packages(args)
    if len(newest_packages) == 0 and len(compile_packages) == 0:
        print("No packages to download, you must specify one package to download at least")
        return []

    file_names = []
    ci = cip.HisiHdfs()
    if len(newest_packages) > 0:
        file_names += ci.download_newest(args.directory, list(newest_packages))
    if len(compile_packages) > 0:
        file_names += ci.download_compile_packages(args.compile.split(',')[0].strip(), args.directory, list(compile_packages))

    return file_names


def install(directory, package_names, install_path):
    shell = eo.AscendShell.create_local()
    for package_name in package_names:
        if cip.PackageType.guess_type_by_name(package_name) == cip.PackageType.FWKACLLIB_ONETRACK:
            logging.warning("try to install package fwkacllib, delete site-packages first")
            if install_path is None:
                shell.exec_command("rm -rf /usr/local/Ascend/fwkacllib/site-packages")
                shell.exec_command("rm -rf /usr/local/Ascend/fwkacllib/python/site-packages/")
            else:
                shell.exec_command("rm -rf {}/fwkacllib/site-packages".format(install_path))
                shell.exec_command("rm -rf {}/fwkacllib/python/site-packages/".format(install_path))
        shell.install(os.path.join(directory, package_name), install_path)


def init_log():
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger('hdfs.client').setLevel(logging.WARNING)


def main():
    init_log()
    args = parse_args(sys.argv[1:])
    if args.version:
        print("Ada {}".format(ada_version))
        return

    package_names = download(args)
    if args.install and len(package_names) > 0:
        install(args.directory, package_names, args.install_path)


if __name__ == "__main__":
    main()

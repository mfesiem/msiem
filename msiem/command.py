# -*- coding: utf-8 -*-
"""
    msiem command
"""

import argparse
try:
    from .config import ESMConfig
except ImportError :
    from config import ESMConfig

def parseArgs():
    parser = argparse.ArgumentParser(description='McAfee SIEM Command Line Interface and Python API',
                usage='Use "msiem --help" for more information',
                formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--version')
    parser.add_argument('--batch')

    commands = parser.add_subparsers()

    config_command = commands.add_parser('config')
    config_command.set_defaults(func=config)
    config_command.add_argument('--list')
    config_command.add_argument('--set')

    return (parser.parse_args())

def config(args):
    c=ESMConfig()
    if args.set is not None :
        if 'auth' in args.set :
            c.setAuth()
            c.write()

def main():
    args = parseArgs()
    args.func(args)

if __name__ == "__main__":
    main()



# _*_ encoding: utf-8 _*_
"""12306

Usage:
    12306 [-gdtkz] from <fcity> to <tcity> on <date>

Options:
    -h, --help      显示帮助页
    -g              高铁
    -d              动车
    -t              特快
    -k              快速
    -z              直达

Example:
    12306 from beijing to shanghai 160508
"""
from docopt import docopt


def command_line_interface():
    arguments = docopt(__doc__)
    print(arguments)

if __name__ == '__main__':
    command_line_interface()

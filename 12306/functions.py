import re
import requests
import sys
from datetime import date
# import datetime
from codecs import open

from prettytable import PrettyTable


class TrainsCollection(object):

    """A set of raw datas from a query."""

    TRAIN_NOT_FOUND = 'No result.'

    headers = '车次 车站 时间 历时 商务 一等 二等 软卧 硬卧 软座 硬座 无座'.split()

    def __init__(self, rows, opts):
        self._rows = rows
        self._opts = opts

    def __repr__(self):
        return '<TrainsCollection size={}>'.format(len(self))

    def __len__(self):
        return len(self._rows)

    def _get_duration(self, row):
        duration = row.get('lishi').replace(':', '小时') + '分钟'
        # take 0 hour , only show minutes
        if duration.startswith('00'):
            return duration[4:]
        # take <10 hours, show 1 bit
        if duration.startswith('0'):
            return duration[1:]
        return duration

    @property
    def trains(self):
        """Filter rows according to `headers`"""
        for row in self._rows:
            train_no = row.get('station_train_code')
            initial = train_no[0].lower()
            if not self._opts or initial in self._opts:
                train = [
                    # Column: '车次'
                    train_no,
                    # Column: '车站'
                    '\n'.join([
                        colored.green(row.get('from_station_name')),
                        colored.red(row.get('to_station_name')),
                    ]),
                    # Column: '时间'
                    '\n'.join([
                        colored.green(row.get('start_time')),
                        colored.red(row.get('arrive_time')),
                    ]),
                    # Column: '历时'
                    self._get_duration(row),
                    # Column: '商务'
                    row.get('swz_num'),
                    # Column: '一等'
                    row.get('zy_num'),
                    # Column: '二等'
                    row.get('ze_num'),
                    # Column: '软卧'
                    row.get('rw_num'),
                    # Column: '硬卧'
                    row.get('yw_num'),
                    # Column: '软座'
                    row.get('rz_num'),
                    # Column: '硬座'
                    row.get('yz_num'),
                    # Column: '无座'
                    row.get('wz_num')
                ]
                yield train

    def pretty_print(self):
        """Use `PrettyTable` to perform formatted outprint."""
        pt = PrettyTable()
        if len(self) == 0:
            pt._set_field_names(['Sorry,'])
            pt.add_row([TRAIN_NOT_FOUND])
        else:
            pt._set_field_names(self.headers)
            for train in self.trains:
                pt.add_row(train)
        print(pt)

def generate_stations() -> object:
    """
    Fetch the code of each railway station from 12306.cn

    Scrawl the code, generate a dictionary named stations in ./stations.py
    :return: No return
    """
    url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8968'
    r = requests.get(url, verify=False)
    pattern = re.compile(r'([\u4e00-\u9fa5]+)\|([A-Z]+)\|([a-z]+)')
    find_results = pattern.finditer(r.text)
    assert find_results is True, 'No match in generating stations dict'
    stations = {}
    for i in find_results:
        stations[i.group(1)] = i.group(2)
        stations[i.group(3)] = i.group(2)

    temp = sys.stdout
    with open('stations.py', 'w', 'utf8') as f:
        sys.stdout = f
        print('# _*_coding: utf-8 _*_')
        print('stations = ', end='')
        print(stations)
    assert isinstance(temp, object)
    sys.stdout = temp


def translate_date(date_input):
    """
    Translate the date input to a datetime.date object

    :param date_input: One string, such as '20161001', '10-3', '161004'
    :return: A datetime.date object as the date input
    """
    # result1 = re.match(r'((\d\d)?(?P<year>\d\d))?(?P<month>([0]?\d)|(11|12))(?P<day>([012]?\d)|(30|31))$', date_input)
    result = re.match(
        r'((\d\d)?(?P<year>\d\d)[-/\\.]?)?(?P<month>((1[012])|[0]?[1-9]))[-/\\.]?(?P<day>([12]\d)|(30|31)|0?[1-9])',
        date_input
    )
    today = date.today()
    period_max = 59

    if result:
        if result.group('year'):
            year = int(result.group('year')) + 2000
        else:
            year = today.year
        month = int(result.group('month'))
        day = int(result.group('day'))
    else:
        print('Input Time Form Error.')
        return None

    date_query = date(year, month, day)

    period = date_query - today
    if period.days < 0:
        print('You cannot back to past.')
        return None
        # return date_query
    elif period.days > period_max:
        print('It is out of the booking period.')
        return None
    else:
        return date_query


class Colored:
    RED = '\033[91m'
    GREEN = '\033[92m'
    RESET = '\033[0m'

    def color_str(self, color, s):
        return '{0}{1}{2}'.format(getattr(self, color), s, self.RESET)

    def red(self, s):
        return self.color_str('RED', s)

    def green(self, s):
        return self.color_str('GREEN', s)


def exit_after_echo(msg, color='red'):
    if color == 'red':
        print(colored.red(msg))
    else:
        print(msg)
    exit(1)

colored = Colored()

if __name__ == '__main__':
    print(translate_date('161120'))
    # generate_stations()

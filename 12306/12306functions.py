import re
import requests
import sys
from datetime import date
# import datetime
from codecs import open


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


if __name__ == '__main__':
    print(translate_date('161120'))
    # generate_stations()

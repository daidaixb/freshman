import re
import requests
import sys
import datetime
from codecs import open


def generate_stations():
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
    result1 = re.match(r'((\d\d)?(?P<year>\d\d))?(?P<month>([0]?\d)|(11|12))(?P<day>([012]?\d)|(30|31))$', date_input)
    result2 = re.match(r'((\d\d)?(?P<year>\d\d)[-|/|\.])?(?P<month>([0]?\d)|(11|12))[-|/|\.](?P<day>([012]?\d)|(30|31))', date_input)
    today = datetime.date.today()
    period_max = 59

    if result1:
        if result1.group('year'):
            year = int(result1.group('year')) + 2000
        else:
            year = today.year
        month = int(result1.group('month'))
        day = int(result1.group('day'))
    elif result2:
        if result2.group('year'):
            year = int(result2.group('year')) + 2000
        else:
            year = today.year
        month = int(result2.group('month'))
        day = int(result2.group('day'))
    else:
        print('Input Time Form Error.')
        return None

    date_query = datetime.date(year, month, day)

    period = date_query - today
    if period.days < 0:
        print('You cannot back to past.')
        return None
    elif period.days > period_max:
        print('It is out of the booking period.')
        return None
    else:
        return date_query


if __name__ == '__main__':
    generate_stations()



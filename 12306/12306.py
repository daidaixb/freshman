# _*_ coding: utf-8 _*_
"""12306

Usage:
    12306 [-gdtkz] from <from> to <to> on <date>

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

import os
import tempfile
import re
import requests
from docopt import docopt
from datetime import date
from collections import OrderedDict

# try:
#     import cPickle as pickle
# except ImportError:
#     import pickle
# from functions.py import exit_after_echo, translate_date, TrainsCollections
# if not os.path.exists('stations.py'):
#     generate_stations()
from functions import exit_after_echo, translate_date, TrainsCollection
from stations import stations

QUERY_URL = 'https://kyfw.12306.cn/otn/lcxxcx/query'

FROM_STATION_NOT_FOUND = 'From station not found.'
TO_STATION_NOT_FOUND = 'To station not found.'
INVALID_DATE = 'Invalid date input.'
TRAIN_NOT_FOUND = 'Sorry, there is no train.'
NO_RESPONSE = 'Sorry, server is not responding'


def cli():
    arguments = docopt(__doc__)
    from_station = arguments['<from>']
    to_station = arguments['<to>']
    date_query = arguments['<date>']
    return TrainQuery(from_station, to_station, translate_date(date_query).isoformat()).query()


class TrainQuery:
    """Class for Train Querying"""
    def __init__(self, from_station, to_station, date_query, opts=None):
        """

        :type from_station: str
        """
        self._from_station = from_station
        self._to_station = to_station
        # assert isinstance(date_query, object)
        self._date_query = date_query
        self._opts = opts

    def __repr__(self):
        return 'TrainQuery from={0} to={} date={}'.format(self._to_station, self._to_station, self._date)

    # @property
    # def stations(self):
    #     filename = 'stations.cache'
    #     _cache_file = os.environ.get('STATIONS_CACHE', os.path.join(tempfile.gettempdir(), filename))
    #     if os.path.exists(_cache_file):
    #         try:
    #             with open(_cache_file, 'rb') as f:
    #                 return pickle.load(f)
    #         except:
    #             pass
    #
    #     file_path = os.path.join(os.path.dirname(__file__), 'data', 'stations.dat')
    #     d = {}
    #     with open(file_path, 'r', encoding='utf8') as f:
    #         for line in f.readlines():
    #             name, code = line.split()
    #             d.setdefault(name, code)
    #
    #     with open(_cache_file, 'wb') as f:
    #         pickle.dump(d, f)
    #
    #     return d

    @property
    def _from_station_code(self):
        code = stations.get(self._from_station)
        if not code:
            exit_after_echo(FROM_STATION_NOT_FOUND)
        return code

    @property
    def _to_station_code(self):
        code = stations.get(self._to_station)
        if not code:
            exit_after_echo(TO_STATION_NOT_FOUND)
        return code

    def query(self):
        params = OrderedDict()
        params['purpose_codes'] = 'ADULT'
        params['queryDate'] = self._date_query
        params['from_station'] = self._from_station_code
        params['to_station'] = self._to_station_code

        r = requests.get(QUERY_URL, params=params, verify=False)

        try:
            rows = r.json()['data']['datas']
        except KeyError:
            rows = []
        except TypeError:
            exit_after_echo(NO_RESPONSE)

        return TrainsCollection(rows, self._opts)

if __name__ == '__main__':
    cli().pretty_print()

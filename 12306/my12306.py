# _*_ coding: utf-8 _*_
"""12306

Usage:
    12306 [-gdtkz] <from> <to> <date>

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
import requests
from collections import OrderedDict
try:
    import cPickle as pickle
except ImportError:
    import pickle
from docopt import docopt
from functions import exit_after_echo, translate_date, TrainsCollection, generate_stations


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
        self.from_station = from_station
        self.to_station = to_station
        self.date_query = date_query
        self._opts = opts
        datapath = os.path.join(os.path.dirname(__file__), 'stations.dat')
        if not os.path.exists(datapath):
            generate_stations()
        with open(datapath, 'rb') as f:
            self._stations = pickle.load(f)
        print(self.from_station, self.to_station, self.date_query)

    def __repr__(self):
        return 'TrainQuery from={0} to={} date={}'.format(self.to_station, self.to_station, self.date_query)

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
    def from_station_code(self):
        code = self._stations.get(self.from_station)
        if not code:
            exit_after_echo(FROM_STATION_NOT_FOUND)
        return code

    @property
    def to_station_code(self):
        code = self._stations.get(self.to_station)
        if not code:
            exit_after_echo(TO_STATION_NOT_FOUND)
        return code

    def query(self):
        params = OrderedDict()
        params['purpose_codes'] = 'ADULT'
        params['queryDate'] = self.date_query
        params['from_station'] = self.from_station_code
        params['to_station'] = self.to_station_code

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

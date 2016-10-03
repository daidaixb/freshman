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

from docopt import docopt
from datetime import date
from 12306functions import generate_stations

if not os.path.exists('stations.py'):
    generate_stations()
from stations import stations


FROM_STATION_NOT_FOUND = 'From station not found.'
TO_STATION_NOT_FOUND = 'To station not found.'
INVALID_DATE = 'Invalid date input.'
TRAIN_NOT_FOUND = 'Sorry, there is no train.'
NO_RESPONSE = 'Sorry, server is not responding'

def cli():
    arguments = docopt(__doc__)
    from_station = stations.get(arguments['<from>'], FROM_STATION_NOT_FOUND)
    to_station = stations.get(arguments['<to>'], TO_STATION_NOT_FOUND)
    date_query = arguments['<date>']


class TrainQuery:
    """Class for Train Query"""
    def __init__(self, from_station, to_station, date_query, opts=None):
        self._from_station = from_station
        self._to_station = to_station
        self._date = date_query
        self._opts = opts

    def __repr__(self):
        return 'TrainQuery from={0} to={} date={}'.format(self._to_station, self._to_station, self._date)

    @property
    def satations(self):




if __name__ == '__main__':
    command_line_interface()

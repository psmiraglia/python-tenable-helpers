"""
Copyright 2022 Paolo Smiraglia <paolo.smiraglia@gmail.com>
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import os
import sys
from datetime import datetime as dt

import click
from tenable.io import TenableIO
from tenable.io.base import TIOEndpoint

from tenable_helpers import commons

try:
    from keys import ACCESS_KEY, SECRET_KEY
except Exception as e:  # noqa
    ACCESS_KEY = os.getenv('ACCESS_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')


class RemediationGoalsAPI(TIOEndpoint):
    def search(self, filters, *args, **kwargs):
        path = 'remediation/goal/search'
        payload = {
            'filter': filters,
            'limit': 200,
            'next': None,
            'sort': [{'property': 'name', 'order': 'desc'}]
        }
        res = self._api.post(path, json=payload)
        return res.json().get('goals', [])

    def create(self, conf, *args, **kwargs):
        path = 'remediation/goal'
        self._api.post(path, json=conf)


class TenableIOExtended(TenableIO):
    @property
    def remediation_goals(self):
        return RemediationGoalsAPI(self)


def build_description(desc_str):
    d = ''
    if desc_str.startswith('@'):
        f = desc_str[1:]
        if not os.path.exists(f):
            print(f'(!) File {f} does not exist')
        else:
            print(f'(*) Load text from file: {f}')
            lines = []
            with open(f, 'r') as fp:
                lines = fp.readlines()
                fp.close()
            d = ''.join(lines)
    else:
        d = desc_str
    return d + '\n\nNote: created via API'


@click.command()
@click.option('-n', '--name', 'g_name', default=None, required=True,
              help='Name of the remediation goal')
@click.option('-d', '--description', 'g_desc', default=None, required=True,
              help='Description of the remediation goal')
@click.option('-c', '--conditions', 'g_cond', default=None, required=True,
              help='Conditions of the remediation goal')
@click.option('-S', '--start-date', 'g_sd', default=None, required=True,
              help='Start date of the remediation goal (YYYY-MM-DD)')
@click.option('-D', '--due-date', 'g_dd', default=None, required=True,
              help='Due date of the remediation goal (YYYY-MM-DD)')
def tio_create_rg(g_name, g_desc, g_cond, g_sd, g_dd):
    # check credentials
    if not ACCESS_KEY:
        print('(!) ACCESS_KEY must be defined')
        sys.exit(1)

    if not SECRET_KEY:
        print('(!) SECRET_KEY must be defined')
        sys.exit(1)

    # parse inpupt parameters
    try:
        description = build_description(g_desc)
        fmt_1 = '%Y-%m-%d'
        fmt_2 = fmt_1 + 'T%H:%M:%S.000Z'
        startdate = int(dt.strptime(g_sd, fmt_1).timestamp())
        duedate = int(dt.strptime(g_dd, fmt_1).timestamp())
        goalduedate = dt.strptime(g_dd, fmt_1).strftime(fmt_2)
        conditions = json.dumps(commons.str_to_json(g_cond))
    except Exception as e:
        print(f'(!) Error: {e}')
        sys.exit(1)

    # init the API
    tio = TenableIOExtended(ACCESS_KEY, SECRET_KEY)

    # create remediation goal
    conf = {
        'name': g_name,
        'description': description,
        'findingfilters': conditions,
        'type': 'Static',
        'status': 'ACTIVE',
        'startdate': startdate,
        'duedate': duedate,
        'goalduedate': {
            'name': 'byFixedDate',
            'value': goalduedate
        }
    }
    tio.remediation_goals.create(conf)

    # get details
    goals = tio.remediation_goals.search({
        'and': [
            {'property': 'name', 'operator': 'eq', 'value': g_name}
        ]
    })
    for g in goals:
        print(f'(*) Remediation goal has been created: {g.get("name")} ({g.get("goaluuid")})')  # noqa

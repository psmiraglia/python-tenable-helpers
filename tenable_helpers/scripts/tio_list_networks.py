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

import csv
import json
import os
import sys

import click
from tenable.io import TenableIO

try:
    from keys import ACCESS_KEY, SECRET_KEY
except Exception as e:  # noqa
    ACCESS_KEY = os.getenv('ACCESS_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')


def as_csv(networks):
    fields = [
        'name',
        'uuid',
        'assets_ttl_days',
        'created',
        'created_by',
        'created_in_seconds',
        'deleted',
        'deleted_by',
        'description',
        'is_default',
        'modified',
        'modified_by',
        'modified_in_seconds',
        'owner_uuid',
        'scanner_count'
    ]
    w = csv.DictWriter(
        sys.stdout,
        fieldnames=fields,
        restval=None,
        quoting=csv.QUOTE_NONNUMERIC
    )
    w.writeheader()
    w.writerows(networks)


def as_json(networks):
    print(
        json.dumps(networks, indent=2, sort_keys=True)
    )


def as_txt(networks):
    for n in networks:
        print(f'Name : {n.get("name")}')
        print(f'ID   : {n.get("uuid")}')
        print(f'URL  : https://cloud.tenable.com/tio/app.html#/settings/sensors/nessus/networks/network-details/{n.get("uuid")}/settings')  # noqa
        print('')


@click.command()
@click.option('--as-json', '_as_json', is_flag=True)
@click.option('--as-csv', '_as_csv', is_flag=True)
def tio_list_networks(_as_json, _as_csv):
    # check credentials
    if not ACCESS_KEY:
        print('(!) ACCESS_KEY must be defined')
        sys.exit(1)

    if not SECRET_KEY:
        print('(!) SECRET_KEY must be defined')
        sys.exit(1)

    # init the API
    tio = TenableIO(ACCESS_KEY, SECRET_KEY)

    # get the networks
    networks = [n for n in tio.networks.list(include_deleted=True)]

    # print the result
    if _as_json:
        as_json(networks)
    elif _as_csv:
        as_csv(networks)
    else:
        as_txt(networks)

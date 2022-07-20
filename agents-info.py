#!/usr/bin/env python3

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

import argparse
import datetime
import logging
import time

from tenable.io import TenableIO

import commons
from keys import ACCESS_KEY, SECRET_KEY

logging.basicConfig(level=logging.INFO)


def never_connect(agents):
    headline = ['Agent Name', 'Linked On']
    rows = []
    for a in agents:
        if a.get('last_connect', -1) < 0:
            name = a.get('name')
            linked_on = time.strftime('%Y-%m-%d',
                                      time.localtime(a.get('linked_on', 0)))
            rows.append((name, linked_on))
    return headline, rows


def plugins_never_update(agents):
    headline = ['Agent Name', 'Linked On', 'Last Connect']
    rows = []
    for a in agents:
        if int(a.get('plugin_feed_id', -1)) < 0:
            name = a.get('name')
            linked_on = time.strftime(
                '%Y-%m-%d',
                time.localtime(a.get('linked_on', 0))
            )
            last_connect = time.strftime(
                '%Y-%m-%d',
                time.localtime(a.get('last_connect', 0))
            )
            rows.append((name, linked_on, last_connect))
    return headline, rows


f = {
    'never_connect': never_connect,
    'plugins_never_update': plugins_never_update
}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--never-connect', action='store_true',
                   help='list agents that never connected after the linking')
    p.add_argument('--plugins-never-update', action='store_true',
                   help='list agents that never had pluging update after the linking')  # noqa
    p.add_argument('--agent-group-id', default=None,
                   help='specify the agent group to get the agents from')
    args = p.parse_args()

    # int the api
    tio = TenableIO(ACCESS_KEY, SECRET_KEY)

    gid = args.agent_group_id
    if not args.agent_group_id:
        # get and select the agent group
        agent_groups = commons.get_agent_groups(tio)
        g = commons.select_agent_group(agent_groups)
        gid = str(g['id'])

    # filter agents
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    for arg in ['never_connect',
                'plugins_never_update']:
        if getattr(args, arg):
            print(f'[{arg}] Start analysis')
            # get and filter agents
            agents = commons.get_agents(tio, ('groups', 'eq', gid))
            headline, rows = f[arg](agents)

            print(f'[{arg}] {len(rows)} agents')

            if len(rows) > 0:
                # save result to file
                out_file = f'{arg}.{gid}.{now}.csv'
                with open(out_file, 'w') as fd:
                    commons.as_csv(fd, headline, rows)
                    fd.close()

                print(f'[{arg}] Result saved: {out_file}')

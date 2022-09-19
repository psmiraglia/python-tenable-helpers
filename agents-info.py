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
import os
import sys
import time

from tenable.io import TenableIO

import commons

try:
    from keys import ACCESS_KEY, SECRET_KEY
except Exception as e:  # noqa
    ACCESS_KEY = os.getenv('ACCESS_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')

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
    if not ACCESS_KEY:
        print('(!) ACCESS_KEY must be defined')
        sys.exit(1)

    if not SECRET_KEY:
        print('(!) SECRET_KEY must be defined')
        sys.exit(1)

    p = argparse.ArgumentParser()
    p.add_argument('--never-connect', action='store_true',
                   help='list agents that never connected after the linking')
    p.add_argument('--plugins-never-update', action='store_true',
                   help='list agents that never had pluging update after the linking')  # noqa
    p.add_argument('--agent-group-id', default=None,
                   help='specify the agent group to get the agents from')
    p.add_argument('--agent-group-name', default=None,
                   help=('specify the agent group to get the agents from '
                         '(ignored if --agent-group-id is used)'))
    args = p.parse_args()

    # int the api
    tio = TenableIO(ACCESS_KEY, SECRET_KEY)

    # obtain group id (gid) and group name (g_name)
    gid = args.agent_group_id
    g_name = args.agent_group_name
    agent_groups = commons.get_agent_groups(tio)
    if not gid:
        if g_name:
            for g in agent_groups:
                if g['name'].lower() == g_name.lower():
                    gid = str(g['id'])
                    break
            if not gid:
                print(f'[E] Unable to find agent group with name {g_name}')
                sys.exit(1)
        else:
            g = commons.select_agent_group(agent_groups)
            gid = str(g['id'])
            g_name = str(g['name'])
    else:
        if g_name:
            print(f'[W] Switch "--agent-group-name {g_name}" will be ignored')
            g_name = None
        for g in agent_groups:
            if str(g['id']).lower() == gid.lower():
                g_name = str(g['name'])
                break
        if not g_name:
            print(f'[E] Unable to find agent group with id {gid}')
            sys.exit(1)

    print(f'[*] Looking info agent group: {g_name} ({gid})')

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

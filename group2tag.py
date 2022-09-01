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

import json

import click
from tenable.io import TenableIO

import commons
from keys import ACCESS_KEY, SECRET_KEY


def _get_agents(tio, g_id, limit, offset):
    res = tio.agent_groups.details(g_id, limit=limit, offset=offset)
    tot = res.get('pagination').get('total')
    agents = [a for a in res.get('agents')]
    return agents, tot


def _get_assets(tio, agents):
    limit = 100
    assets = []
    f = {
        'and': [
            {
                'property': 'host_name',
                'operator': 'eq',
                'value': [a.get('name') for a in agents]
            },
            {
                'property': 'sources',
                'operator': 'eq',
                'value': ['NESSUS_AGENT']
            }
        ]
    }

    # first page
    res = tio.v3.explore.assets.search_all(filter=f,
                                           limit=limit,
                                           return_resp=True)
    data = json.loads(res.text)

    _assets = [a for a in data.get('assets')]
    if len(_assets) > 0:
        assets += _assets
        print(f'(*) Got {len(assets)} assets')
    token = data.get('pagination').get('next')

    # other pages
    while token:
        res = tio.v3.explore.assets.search_all(filter=f, limit=limit, next=token, return_resp=True)  # noqa
        data = json.loads(res.text)

        _assets = [a for a in data.get('assets')]
        if len(_assets) > 0:
            assets += _assets
            print(f'Got {len(assets)} assets')
        token = data.get('pagination').get('next')

    # return assets
    return assets


def _assign_tag(tio, tag_id, tag_name, assets):
    tio.tags.assign([a.get('id') for a in assets], [tag_id])
    print(f'(*) Tag "{tag_name}" has been assigned to {"|".join([a.get("name") for a in assets])}')  # noqa


@click.command()
@click.option('-n', '--name', 'g_name',
              default=None, help='Name of the agent group')
@click.option('-i', '--id', 'g_id',
              default=None, help='ID of the agent group')
def g2t(g_name, g_id):
    # init the API
    tio = TenableIO(ACCESS_KEY, SECRET_KEY)

    # select the group
    if (not g_name) or (not g_id):
        groups = commons.get_agent_groups(tio)
        g = commons.select_agent_group(groups)
        g_name = g.get('name')
        g_id = g.get('id')

    # create tag
    tag = commons.create_tag(tio, 'AgentGroup', g_name, True)
    tag_name = f'{tag.get("category_name")}:{tag.get("value")}'
    tag_id = tag.get('uuid')
    print(f'(*) Tag "{tag_name}" with ID "{tag_id}" has been created')

    #
    # iterate over agents in agent group
    #
    agents = []
    offset = 0
    limit = 100
    got = 0

    # first page
    agents, tot = _get_agents(tio, g_id, limit, offset)
    got += len(agents)
    print(f'(*) Got {got} over {tot} agents')
    assets = _get_assets(tio, agents)
    _assign_tag(tio, tag_id, tag_name, assets)

    # other pages
    while got < tot:
        offset += limit
        agents, tot = _get_agents(tio, g_id, limit, offset)
        got += len(agents)
        print(f'(*) Got {got} over {tot} agents')
        assets = _get_assets(tio, agents)
        _assign_tag(tio, tag_id, tag_name, assets)


if __name__ == '__main__':
    g2t()

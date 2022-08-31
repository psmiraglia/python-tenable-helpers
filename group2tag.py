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

import click
from tenable.io import TenableIO

import commons
from keys import ACCESS_KEY, SECRET_KEY


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

    # get agents from group
    _agents = tio.agent_groups.details(g_id)['agents']
    agents = [a for a in _agents]

    # get assets from agents
    _assets = tio.v3.explore.assets.search_all(filter={
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
    })
    assets = [a for a in _assets]

    # create tag
    tag = commons.create_tag(tio, 'AgentGroup', g_name, True)
    tag_name = f'{tag.get("category_name")}:{tag.get("value")}'
    tag_id = tag.get('uuid')
    print(f'(*) Tag "{tag_name}" with ID "{tag_id}" has been created')

    # assign tag
    tio.tags.assign([a.get('id') for a in assets], [tag_id])
    print(f'(*) Tag "{tag_name}" has been assigned to...')
    for name in [a.get('name') for a in assets]:
        print(f'(+) {name}')


if __name__ == '__main__':
    g2t()

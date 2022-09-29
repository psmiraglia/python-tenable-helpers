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
import logging
import os
import sys

LOG = logging.getLogger(__name__)

#
# Helpers
#


def as_csv(fd, headline, rows):
    w = csv.writer(fd, quoting=csv.QUOTE_ALL)
    w.writerow(headline)
    for row in rows:
        w.writerow(row)


def str_to_json(json_str):
    f = {}
    try:
        if json_str.startswith('@'):
            # load filters from file
            ffile = json_str[1:]
            if not os.path.exists(ffile):
                LOG.error(f'{ffile} does not exist')
            else:
                LOG.debug(f'Load JSON from file ({ffile})')
                with open(ffile, 'r') as fp:
                    f = json.load(fp)
                    fp.close()
        else:
            # load filters from string
            LOG.debug(f'Load JSON from string ({json_str})')
            f = json.loads(json_str)
    except Exception as e:
        LOG.error(f'Unable to load JSON string: {e}')
        sys.exit(1)

    print(f'(*) JSON: {json.dumps(f)}')
    return f

#
# Agent Group
#


def get_agent_groups(tio):
    ag = []
    try:
        ag = tio.agent_groups.list()
    except Exception as e:
        LOG.error(e)
    return ag


def select_agent_group(agent_groups):
    idx = 1
    ag_size = len(agent_groups)
    prompt = f'Select the agent group ({idx}-{ag_size}): '

    # build the menu
    groups = {}
    for g in sorted(agent_groups, key=lambda d: d['name']):
        groups[str(idx)] = g
        data = f'{g["name"]} (id: {g["id"]})'
        if ag_size < 10:
            line = f'[{idx}] {data}'
        elif ag_size >= 10 and ag_size < 100:
            line = f'[{idx:2}] {data}'
        elif ag_size >= 100 and ag_size < 1000:
            line = f'[{idx:3}] {data}'
        else:
            line = f'[{idx:4}] {data}'
        print(line)
        idx += 1

    # make selection
    choice = input(prompt)
    while choice not in groups:
        print(f'[!] Invalid choice: {choice}')
        choice = input(prompt)

    return groups.get(choice)

#
# Agent
#


def get_agents(tio, *filters):
    agents = []
    try:
        agents = tio.agents.list(*filters)
    except Exception as e:
        LOG.error(e)
    return agents

#
# Tags
#


def create_tag(tio, category, name, delete_assignments=False):
    def _cb(tio, assets, tag_uuid):
        _assets_id = [a.get('id') for a in assets]
        _assets_name = [a.get('name') for a in assets]
        _tags = [tag_uuid]
        print(f'(*) Tag "{category}:{name}" has been removed from {"|".join(_assets_name)}')  # noqa
        tio.tags.unassign(_assets_id, _tags)

    tag = next(tio.tags.list(('category_name', 'eq', category),
                             ('value', 'eq', name),
                             limit=1), None)
    if tag:
        if delete_assignments:
            filters = {'and': [{'property': 'tags',
                                'operator': 'eq',
                                'value': [tag.get('uuid')]}]}
            find_assets(tio, filters, _cb, tag.get('uuid'))
        else:
            print(f'(!) Tag {category}:{name} already exists')
    else:
        description = 'Created via API'
        tag = tio.tags.create(category, name, description=description,
                              category_description=description)

    return tag


#
# Assets
#

def find_assets(tio, filters, cb, *args, **kwargs):
    assets = []

    limit = 100
    sort = []
    fields = []
    pagination = None
    token = None

    # first call
    res = tio.v3.explore.assets.search_all(filter=filters,
                                           sort=sort,
                                           fields=fields,
                                           limit=limit,
                                           return_resp=True)
    data = json.loads(res.text)
    _assets = data.get('assets', [])
    if len(_assets) > 0:
        if cb:
            cb(tio, _assets, *args, **kwargs)
        assets += _assets
    pagination = data.get('pagination')
    if pagination:
        token = pagination.get('next')
    else:
        token = None

    # get other pages of results (if any)
    while token:
        res = tio.v3.explore.assets.search_all(filter=filters,
                                               sort=sort,
                                               fields=fields,
                                               limit=limit,
                                               return_resp=True,
                                               next=token)
        data = json.loads(res.text)
        _assets = data.get('assets', [])
        if len(_assets) > 0:
            if cb:
                cb(tio, _assets, *args, **kwargs)
            assets += _assets
        pagination = data.get('pagination')
        if pagination:
            token = pagination.get('next')
        else:
            token = None

    return assets

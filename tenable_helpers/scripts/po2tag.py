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
import logging
import os
import re
import sys

import click
from tenable.io import TenableIO

from tenable_helpers import commons

try:
    from keys import ACCESS_KEY, SECRET_KEY
except Exception as e:  # noqa
    ACCESS_KEY = os.getenv('ACCESS_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')

# setup logging
LOG = logging.getLogger(__name__)


def assign_tag(tio, tag_id, tag_name, assets):
    tio.tags.assign([a.get('id') for a in assets], [tag_id])
    print(f'(*) Tag "{tag_name}" has been assigned to {"|".join([a.get("name") for a in assets])}')  # noqa


def parse_output(output, regex):
    result = False
    p = re.compile(regex, re.MULTILINE | re.IGNORECASE)
    m = p.search(output)
    if m:
        result = True
    return result


def get_assets_from_findings(findings, regex, regex_negative):
    assets = []
    for f in findings:
        output = f.get('output', '')
        do_append = parse_output(output, regex)
        if regex_negative:
            do_append = not do_append
        if do_append:
            assets.append(f.get('asset'))
    return assets


def find_assets_and_assign_tag(tio, tag_name, tag_id, filters, regex,
                               regex_negative, *args, **kwargs):
    assets = []
    all_assets = []

    limit = 100
    sort = [('severity', 'desc')]
    fields = ['asset.name', 'asset.id', 'output', 'severity']

    pagination = None
    token = None

    # get first page of results
    res = tio.v3.explore.findings.search_host(filter=filters,
                                              sort=sort,
                                              fields=fields,
                                              limit=limit,
                                              return_resp=True)
    data = json.loads(res.text)
    findings = data.get('findings', [])
    assets = get_assets_from_findings(findings, regex, regex_negative)
    if len(assets) > 0:
        _assets = [a for a in assets if a.get('id') not in all_assets]
        if len(_assets) > 0:
            assign_tag(tio, tag_id, tag_name, _assets)
            all_assets += [a.get('id') for a in _assets]
    pagination = data.get('pagination')
    if pagination:
        token = pagination.get('next')
    else:
        token = None

    # get other pages of results (if any)
    while token:
        res = tio.v3.explore.findings.search_host(filter=filters,
                                                  sort=None,
                                                  fields=fields,
                                                  limit=limit,
                                                  return_resp=True,
                                                  next=token)
        data = json.loads(res.text)
        findings = data.get('findings', [])
        assets = get_assets_from_findings(findings, regex, regex_negative)
        if len(assets) > 0:
            _assets = [a for a in assets if a.get('id') not in all_assets]
            if len(_assets) > 0:
                assign_tag(tio, tag_id, tag_name, _assets)
                all_assets += [a.get('id') for a in _assets]
        pagination = data.get('pagination')
        if pagination:
            token = pagination.get('next')
        else:
            token = None


def build_filters(filters_str):
    f = {}
    try:
        if filters_str.startswith('@'):
            # load filters from file
            ffile = filters_str[1:]
            if not os.path.exists(ffile):
                LOG.error(f'{ffile} does not exist')
            else:
                LOG.debug(f'Load filters from file ({ffile})')
                with open(ffile, 'r') as fp:
                    f = json.load(fp)
                    fp.close()
        else:
            # load filters from string
            LOG.debug(f'Load filters from string ({filters_str})')
            f = json.loads(filters_str)
    except Exception as e:
        LOG.error(f'Unable to load filters string: {e}')
        sys.exit(1)

    print(f'(*) Filter: {json.dumps(f)}')
    return f


def build_regex(regex_str):
    # '^[\s]*installed version[\s]*:[\s]*69\.0\.1$'
    s = ""
    try:
        if regex_str.startswith('@'):
            LOG.debug(f'Load regex from file ({regex_str})')
            with open(regex_str[1:], 'r') as fp:
                s = fp.readlines()[0][:-1].strip()
                fp.close()
        else:
            LOG.debug(f'Load regex from string ({regex_str})')
            s = regex_str
    except Exception as e:
        LOG.error(f'Unable to load regex: {e}')
        sys.exit(1)

    regex = r'%s' % s
    print(f'(*) Regex: {regex}')
    return regex


@click.command()
@click.option('-c', '--tag-category', 't_category', default=None,
              help='Name of the tag category', required=True)
@click.option('-n', '--tag-name', 't_name', default=None,
              help='Name of the tag', required=True)
@click.option('-e', '--regex', 'regex_str', default=None,
              help='Regex to parse the plugin output', required=True)
@click.option('--regex-negative', 'regex_negative', is_flag=True,
              help='Use regex as negative')
@click.option('-f', '--filters', 'filters_str', default=None,
              help='Assets filters', required=True)
def po2tag(t_category, t_name, regex_str, regex_negative, filters_str):
    # check credentials
    if not ACCESS_KEY:
        print('(!) ACCESS_KEY must be defined')
        sys.exit(1)

    if not SECRET_KEY:
        print('(!) SECRET_KEY must be defined')
        sys.exit(1)

    # build filters and regex
    filters = build_filters(filters_str)
    regex = build_regex(regex_str)

    # init the API
    tio = TenableIO(ACCESS_KEY, SECRET_KEY)

    # create tag
    tag = commons.create_tag(tio, t_category, t_name, True)
    tag_name = f'{tag.get("category_name")}:{tag.get("value")}'
    tag_id = tag.get('uuid')
    print(f'(*) Tag "{tag_name}" with ID "{tag_id}" has been created')

    # find assets and assign tag
    find_assets_and_assign_tag(tio, tag_name, tag_id, filters, regex,
                               regex_negative)

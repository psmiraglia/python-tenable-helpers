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
import logging

LOG = logging.getLogger(__name__)

#
# Helpers
#


def as_csv(fd, headline, rows):
    w = csv.writer(fd, quoting=csv.QUOTE_ALL)
    w.writerow(headline)
    for row in rows:
        w.writerow(row)

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
    prompt = f'[<] Select the agent group ({idx}-{ag_size}): '

    # build the menu
    groups = {}
    for g in agent_groups:
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

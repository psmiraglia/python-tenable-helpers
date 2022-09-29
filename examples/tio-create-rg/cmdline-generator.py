#!/usr/bin/env python3

import json
import os
import sys

BIN = 'tio-create-rg'

def conditions(goal, ring):
    return {
        'and': [
            {
              'id': 'severity',
              'operator': 'neq',
              'value': [0],
              'isFilterSet': True
            },
            {
              'id': 'asset.tags',
              'operator': 'eq',
              'value': ring.get('tags'),
              'isFilterSet': True
            },
            {
              'id': 'definition.name',
              'operator': 'wc',
              'value': goal.get('conditions'),
              'isFilterSet': True
            }
        ]
    }


if __name__ == '__main__':
    g_file = sys.argv[1]
    z_file = sys.argv[2]
    n_prefix = sys.argv[3]
    sd = sys.argv[4]
    dd = sys.argv[5]
    
    outdir = 'files'
    try:
        os.mkdir(outdir)
    except FileExistsError as e:
        print(f'(!) Warning: {e}')
    except Exception as e:
        print(f'(!) Error: {e}')
        sys.exit(1)

    GOALS = {}
    with open(g_file, 'r') as fp:
        GOALS = json.load(fp)
        fp.close()
    
    ZONES = {}
    with open(z_file, 'r') as fp:
        ZONES = json.load(fp)
        fp.close()

    for g in GOALS:
        goal = GOALS.get(g)

        desc_file = f'{outdir}/{g}.txt'
        label = goal.get('label')
        desc = goal.get('description', f'Update {label} to the latest available version')
        with open(desc_file, 'w') as fp:
            fp.write(desc + '\n')
            fp.close()

        for z in ZONES:
            zone = ZONES.get(z)
            rings = zone.get('rings')
            for r in rings:
                ring = rings.get(r)

                cond_file = f'{outdir}/{g}-{z}-{r}.json'
                with open(cond_file, 'w') as fp:
                    json.dump(conditions(goal, ring), fp, indent=2)
                    fp.close()

                name = f'{n_prefix} {goal.get("label")} ({zone.get("label")}, {ring.get("label")})'
                cmdline = f'{BIN} -n "{name}" -d @{desc_file} -c @{cond_file} -S {sd} -D {dd}'
                print(f'{cmdline}')

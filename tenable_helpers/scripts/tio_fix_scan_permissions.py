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

import click
from tenable.io import TenableIO

try:
    from keys import ACCESS_KEY, SECRET_KEY
except Exception as e:  # noqa
    ACCESS_KEY = os.getenv('ACCESS_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')

PERMISSIONS = {
    '0': 'NO ACCESS',
    '16': 'CAN VIEW',
    '32': 'CAN EXECUTE',
    '64': 'CAN EDIT',
    '128': 'OWNER'
}


def load_acls(acls_file):
    acls = None
    with open(acls_file, 'r') as fp:
        acls = json.load(fp)
        fp.close()
    return acls


def fix_permissions(tio, scan, owner, acls):
    scan_id = scan.get('id')
    scan_name = scan.get('name')
    print(f'(*) Scan: {scan_name} ({scan_id})')

    # remove existing permissions
    permissions = tio.permissions.list('scan', scan_id)
    print(f'(*) Current permissions:\n{json.dumps(permissions, indent=2)}')

    for p in permissions:
        otype = p.get('type')
        if otype != 'default':
            oid = p.get('id')
            if otype == 'user':
                try:
                    o = tio.users.details(oid)
                    # print(f'(*) Object found (user): {o.get("name")} ({o.get("id")})')  # noqa
                except Exception:
                    print(f'(!) Object with id {oid} not found')
            elif otype == 'group':
                o_found = False
                for o in tio.groups.list():
                    if oid == o.get('id'):
                        o_found = True
                        # print(f'(*) Object found (group): {o.get("name")} ({o.get("id")})')  # noqa
                        break
                if not o_found:
                    print(f'(!) Object with id {oid} not found')
            else:
                pass

            operm = p.get('permissions')
            operm_label = PERMISSIONS.get(str(operm))
            print(f'(*) Remove permission "{operm_label}" for {otype} "{o.get("name")}" ({oid})')  # noqa
            acl = {'type': otype, 'id': oid, 'permissions': 0}
            tio.permissions.change('scan', scan_id, acl)

    if owner:
        # set the new acls and change the ownership
        owner_id = owner.get('id')
        owner_name = owner.get('name')
        print(f'(*) Set ownership: {owner_name} ({owner_id})')
        print(f'(*) Set ACLs: {json.dumps(acls)}')
        tio.scans.configure(scan_id, owner_id=owner_id, acls=acls)

    else:
        # set the new acls
        print(f'(*) Set ACLs: {json.dumps(acls)}')
        tio.scans.configure(scan_id, acls=acls)

    # get the new permissions
    permissions = tio.permissions.list('scan', scan_id)
    print(f'(*) New permissions:\n{json.dumps(permissions, indent=2)}')


@click.command()
@click.option('-s', '--scan-id', '_scan_id', default=None,
              help='Id of the scanner to be fixed (ignored if --folder-id is used).')  # noqa
@click.option('-f', '--folder-id', '_folder_id', default=None,
              help='Id of the folder that contains scans to be fixed.')
@click.option('-a', '--acls-file', '_acls_file', default=None,
              help='Path to JSON file that contains the new ACLs.')
@click.option('-o', '--owner-id', '_owner_id', default=None,
              help='Id of the user that will be new owner.')
@click.option('-i', '--interactive', '_interactive', is_flag=True,
              help='Run the script interactively.')
def tio_fix_scan_permissions(_scan_id, _folder_id, _acls_file, _owner_id, _interactive):  # noqa
    if (not _scan_id) and (not _folder_id):
        print('(!) Option --scanner-id or --folder-id must be set')
        sys.exit(1)

    if not _acls_file:
        print('(!) Option --acls-file  must be set')
        sys.exit(1)

    print('\n----- PRELIMINARY CHECKS -----\n')
    # check credentials
    if not ACCESS_KEY:
        print('(!) ACCESS_KEY must be defined')
        sys.exit(1)

    if not SECRET_KEY:
        print('(!) SECRET_KEY must be defined')
        sys.exit(1)

    # load the ACLs file
    if not os.path.exists(_acls_file):
        print(f'(!) ACLs file does not exist: {_acls_file}')
        sys.exit(1)
    else:
        acls = load_acls(_acls_file)

    # init the API
    tio = TenableIO(ACCESS_KEY, SECRET_KEY)

    # check if owner exists
    owner = None
    if _owner_id:
        try:
            owner = tio.users.details(_owner_id)
            print(f'(*) Owner found: {owner.get("name")} ({owner.get("id")})')
        except Exception:
            print(f'(!) Owner with ID {_owner_id} does not exist')
            sys.exit(1)

    if _folder_id:
        folder_exists = False
        folder_id = None
        folder_name = None
        for folder in tio.folders.list():
            folder_id = folder.get('id')
            if folder_id == int(_folder_id):
                folder_exists = True
                folder_name = folder.get('name')
                print(f'(*) Folder found: {folder_name} ({folder_id})')
                break

        if not folder_exists:
            print(f'(!) Folder with ID {_folder_id} does not exist')
            sys.exit(1)

        print('\n----- FIX PERMISSIONS -----\n')

        # fix permissions
        for scan in tio.scans.list(folder_id=folder_id):
            fix_permissions(tio, scan, owner, acls)
            if _interactive:
                print('\n')
                input('Press any key to continue...\n')
    else:
        # check if the scan exists
        scan_exists = False
        scan = None
        scan_id = None
        scan_name = None
        for scan in tio.scans.list():
            scan_id = scan.get('id')
            if scan_id == int(_scan_id):
                scan_exists = True
                scan_name = scan.get('name')
                print(f'(*) Scan found: {scan_name} ({scan_id})')
                break

        if not scan_exists:
            print(f'(!) Scan with ID {_scan_id} does not exist')
            sys.exit(1)

        print('\n----- FIX PERMISSIONS -----\n')

        # fix permissions
        fix_permissions(tio, scan, owner, acls)

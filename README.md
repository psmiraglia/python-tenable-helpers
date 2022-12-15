# Tenable.io helpers

Collection of Python scripts to interact with Tenable.io via API.

* [tio-group2tag](#tio-group2tag)
* [tio-po2tag](#tio-po2tag)
* [tio-create-rg](#tio-create-rg)
* [tio-list-networks](#tio-list-networks)

## How to set API credentials

Obtain `ACCESS_KEY` and `SECRET_KEY` from the Tenable.io console and save them in `keys.py` file

~~~.bash
$ cat <<EOF > keys.py
ACCESS_KEY = 'HERE YOUR ACCESS KEY'
SECRET_KEY = 'HERE YOUR SECRET KEY'
EOF
~~~

Alternatively, you can set them as environment variables

~~~.bash
$ export ACCESS_KEY="HERE YOUR ACCESS KEY"
$ export SECRET_KEY="HERE YOUR SECRET KEY"
~~~

If you use Docker, set them in the environment file

~~~.bash
$ cat <<EOF > Docker.env
ACCESS_KEY=HERE YOUR ACCESS KEY
SECRET_KEY=HERE YOUR SECRET KEY
EOF
~~~

## How to install

You can use a Python virtual environment

~~~.bash
$ virtualenv -p python3 .venv
$ . .venv/bin/activate
$ pip install -r requirements.txt
$ pip install -e .
~~~

or build the Docker image

~~~.bash
$ make docker

# or

$ docker build --tag psmiraglia/tenable-helpers .
~~~

## How to use

### agents-info.py (it will be soon removed)

Obtain information about linked agents.

~~~.bash
$ ./agents-info.py -h
usage: agents-info.py [-h] [--never-connect] [--plugins-never-update]
                      [--agent-group-id AGENT_GROUP_ID]
                      [--agent-group-name AGENT_GROUP_NAME]

optional arguments:
  -h, --help            show this help message and exit
  --never-connect       list agents that never connected after the linking
  --plugins-never-update
                        list agents that never had pluging update after the
                        linking
  --agent-group-id AGENT_GROUP_ID
                        specify the agent group to get the agents from
  --agent-group-name AGENT_GROUP_NAME
                        specify the agent group to get the agents from
                        (ignored if --agent-group-id is used)
~~~

Example of execution

~~~.bash
$ ./agents-info.py --never-connect --plugins-never-update --agent-group-id 123456
[never_connect] Start analysis
[never_connect] 6 agents
[never_connect] Result saved: never_connect.123456.20220720180812.csv
[plugins_never_update] Start analysis
[plugins_never_update] 164 agents
[plugins_never_update] Result saved: plugins_never_update.123456.20220720180812.csv
~~~

~~~.bash
$ ./agents-info.py --never-connect --plugins-never-update
[1] Server (id: 654321)
[2] Client (id: 123456)
[3] DMZ (id: 112233)
[<] Select the agent group (1-3): 2
[never_connect] Start analysis
[never_connect] 6 agents
[never_connect] Result saved: never_connect.123456.20220720180812.csv
[plugins_never_update] Start analysis
[plugins_never_update] 164 agents
[plugins_never_update] Result saved: plugins_never_update.123456.20220720180812.csv
~~~

### tio-group2tag

Create tag from agent group and assign it to related assets

~~~.bash
$ tio-group2tag --help
Usage: tio-group2tag [OPTIONS]

Options:
  -n, --name TEXT  Name of the agent group
  -i, --id TEXT    ID of the agent group
  --help           Show this message and exit.
~~~

Examples of execution

~~~.bash
$ tio-group2tag
[1] Server (id: 112233)
[2] Client (id: 112234)
[3] DMZ (id: 112235)
Select the agent group (1-3): 3
(*) Tag "AgentGroup:DMZ" with ID "00000000-0000-0000-0000-000000000000" has been created
(*) Got 3 over 3 agents
(*) Got 3 assets
(*) Tag "AgentGroup:DMZ" has been assigned to sql01|sql02|webserver12

~~~

~~~.bash
$ docker run -ti --rm --env-file Docker.env psmiraglia/tenable-helpers tio-group2tag --name DMZ --id 112235
(*) Tag "AgentGroup:DMZ" with ID "00000000-0000-0000-0000-000000000000" has been created
(*) Got 3 over 3 agents
(*) Got 3 assets
(*) Tag "AgentGroup:DMZ" has been assigned to sql01|sql02|webserver12
~~~

### tio-po2tag

Create tag by parsing a plugin output and assign it to related assets

~~~.bash
$ tio-po2tag --help
Usage: tio-po2tag [OPTIONS]

Options:
  -c, --tag-category TEXT  Name of the tag category  [required]
  -n, --tag-name TEXT      Name of the tag  [required]
  -e, --regex TEXT         Regex to parse the plugin output  [required]
  --regex-negative         Use regex as negative
  -f, --filters TEXT       Assets filters  [required]
  --help                   Show this message and exit.
~~~

Examples of execution

~~~.bash
$ tio-po2tag -c 'Firefox' -n '104.x' -f @po2tag/filters-20811.json --regex @po2tag/regex-20811-firefox-104.txt
(*) Filter: {"and": [{"property": "severity", "operator": "eq", "value": [0]}, {"property": "definition.id", "operator": "eq", "value": ["20811"]}]}
(*) Regex: ^mozilla firefox.*\[version 104(\.\d{1,})*\].*$
(*) Tag "Firefox:104.x" with ID "f03fd7f9-ea0b-47a9-a0fb-48435d265e8a" has been created
(*) Tag "Firefox:104.x" has been assigned to cli1
~~~

~~~.bash
$ docker run -ti --rm -v "$(pwd)/po2tag:/data:ro" --env-file Docker.env psmiraglia/tenable-helpers tio-po2tag -c 'Firefox' -n '104.x' -f @/data/filters-20811.json --regex '^mozilla firefox.*\[version 104(\.\d{1,})*\].*$'
(*) Filter: {"and": [{"property": "severity", "operator": "eq", "value": [0]}, {"property": "definition.id", "operator": "eq", "value": ["20811"]}]}
(*) Regex: ^mozilla firefox.*\[version 104(\.\d{1,})*\].*$
(*) Tag "Firefox:104.x" with ID "f03fd7f9-ea0b-47a9-a0fb-48435d265e8a" has been created
(*) Tag "Firefox:104.x" has been assigned to cli1
~~~

~~~.bash
$ tio-po2tag -c 'Firefox' -n 'NOT-104.x' -f @po2tag/filters-20811.json --regex @po2tag/regex-20811-firefox-104.txt --regex-negative
(*) Filter: {"and": [{"property": "severity", "operator": "eq", "value": [0]}, {"property": "definition.id", "operator": "eq", "value": ["20811"]}]}
(*) Regex: ^mozilla firefox.*\[version 104(\.\d{1,})*\].*$
(*) Tag "Firefox:104.x" with ID "f03fd7f9-ea0b-47a9-a0fb-48435d265e8a" has been created
(*) Tag "Firefox:104.x" has been assigned to cli12|cli23
~~~

### tio-create-rg

Create remediation goals

~~~.bash
$ tio-create-rg --help
Usage: tio-create-rg [OPTIONS]

Options:
  -n, --name TEXT         Name of the remediation goal  [required]
  -d, --description TEXT  Description of the remediation goal  [required]
  -c, --conditions TEXT   Conditions of the remediation goal  [required]
  -S, --start-date TEXT   Start date of the remediation goal (YYYY-MM-DD)
                          [required]
  -D, --due-date TEXT     Due date of the remediation goal (YYYY-MM-DD)
                          [required]
  --help                  Show this message and exit.

~~~

Examples of usage

~~~.bash
$ tio-create-rg --name MyRemediationGoal --description @tio-create-rg/description.txt -c @tio-create-rg/conditions.json -S '2022-09-21' -D '2022-09-25'
(*) Load text from file: tio-create-rg/description.txt
(*) JSON: {"and": [{"id": "severity", "operator": "neq", "value": [0], "isFilterSet": true}, {"id": "state", "operator": "neq", "value": ["FIXED"], "isFilterSet": true}, {"id": "definition.name", "operator": "wc", "value": ["*adobe reader*"], "isFilterSet": true}]}
(*) Remediation goal has been created: MyRemediationGoal (1a322a5c-d92d-428e-9353-510953d45ac9)
~~~

~~~.bash
$ tio-create-rg --name MyRemediationGoal --description "My inline description" -c @tio-create-rg/conditions.json -S '2022-09-21' -D '2022-09-25'
(*) JSON: {"and": [{"id": "severity", "operator": "neq", "value": [0], "isFilterSet": true}, {"id": "state", "operator": "neq", "value": ["FIXED"], "isFilterSet": true}, {"id": "definition.name", "operator": "wc", "value": ["*adobe reader*"], "isFilterSet": true}]}
(*) Remediation goal has been created: MyRemediationGoal (1a322a5c-d92d-428e-9353-510953d45ac9)
~~~

~~~.bash
$ tio-create-rg --name MyRemediationGoal --description @tio-create-rg/description.txt -c '{"and": [{"id": "severity", "operator": "neq", "value": [0], "isFilterSet": true}, {"id": "state", "operator": "neq", "value": ["FIXED"], "isFilterSet": true}, {"id": "definition.name", "operator": "wc", "value": ["*adobe reader*"], "isFilterSet": true}]}' -S '2022-09-21' -D '2022-09-25'
(*) Load text from file: description.txt
(*) JSON: {"and": [{"id": "severity", "operator": "neq", "value": [0], "isFilterSet": true}, {"id": "state", "operator": "neq", "value": ["FIXED"], "isFilterSet": true}, {"id": "definition.name", "operator": "wc", "value": ["*adobe reader*"], "isFilterSet": true}]}
(*) Remediation goal has been created: MyRemediationGoal (1a322a5c-d92d-428e-9353-510953d45ac9)
~~~

### tio-list-networks

List all the defined networks (also the "deleted" ones).

~~~.bash
$ tio-list-networks --help
Usage: tio-list-networks [OPTIONS]

Options:
  --as-json
  --as-csv
  --help     Show this message and exit.
~~~

Examples of usage

~~~.bash
$ tio-list-networks
Name : APAC
ID   : faa0a5e9-574c-4995-b18a-41c601bd8b72
URL  : https://cloud.tenable.com/tio/app.html#/settings/sensors/nessus/networks/network-details/faa0a5e9-574c-4995-b18a-41c601bd8b72/settings

Name : EMEA
ID   : 315b8469-1049-4806-819f-d502cc28381b
URL  : https://cloud.tenable.com/tio/app.html#/settings/sensors/nessus/networks/network-details/315b8469-1049-4806-819f-d502cc28381b/settings
~~~

~~~.bash
$ tio-list-networks --as-json
[
  {
    "assets_ttl_days": 180,
    "created": 1665043358063,
    "created_by": "c3e4a104-8957-41e3-93c0-9a54dc892b49",
    "created_in_seconds": 1665043358,
    "description": "",
    "is_default": false,
    "modified": 1665656055675,
    "modified_by": "c3e4a104-8957-41e3-93c0-9a54dc892b49",
    "modified_in_seconds": 1665656055,
    "name": "APAC",
    "owner_uuid": "c3e4a104-8957-41e3-93c0-9a54dc892b49",
    "scanner_count": 5,
    "uuid": "faa0a5e9-574c-4995-b18a-41c601bd8b72"
  },
  {
    "assets_ttl_days": 180,
    "created": 1665043415366,
    "created_by": "c3e4a104-8957-41e3-93c0-9a54dc892b49",
    "created_in_seconds": 1665043415,
    "description": "",
    "is_default": false,
    "modified": 1665656062571,
    "modified_by": "c3e4a104-8957-41e3-93c0-9a54dc892b49",
    "modified_in_seconds": 1665656062,
    "name": "EMEA",
    "owner_uuid": "c3e4a104-8957-41e3-93c0-9a54dc892b49",
    "scanner_count": 1,
    "uuid": "315b8469-1049-4806-819f-d502cc28381b"
  }
] 
~~~

## References

* [pyTenable](https://pytenable.readthedocs.io/en/stable/)
* [Tenable API](https://developer.tenable.com/reference/navigate)

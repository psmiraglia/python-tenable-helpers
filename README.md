# Tenable.io helpers

Collection of Python scripts to interact with Tenable.io via API.

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

### group2tag

Create tag from agent group and assign it to related assets

~~~.bash
$ group2tag --help
Usage: group2tag.py [OPTIONS]

Options:
  -n, --name TEXT  Name of the agent group
  -i, --id TEXT    ID of the agent group
  --help           Show this message and exit.
~~~

Examples of execution

~~~.bash
$ group2tag
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
$ docker run -ti --rm --env-file Docker.env psmiraglia/tenable-helpers group2tag --name DMZ --id 112235
(*) Tag "AgentGroup:DMZ" with ID "00000000-0000-0000-0000-000000000000" has been created
(*) Got 3 over 3 agents
(*) Got 3 assets
(*) Tag "AgentGroup:DMZ" has been assigned to sql01|sql02|webserver12
~~~

### po2tag

Create tag by parsing a plugin output and assign it to related assets

~~~.bash
$ po2tag --help
Usage: po2tag.py [OPTIONS]

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
$ po2tag -c 'Firefox' -n '104.x' -f @po2tag/filters-20811.json --regex @po2tag/regex-20811-firefox-104.txt
(*) Filter: {"and": [{"property": "severity", "operator": "eq", "value": [0]}, {"property": "definition.id", "operator": "eq", "value": ["20811"]}]}
(*) Regex: ^mozilla firefox.*\[version 104(\.\d{1,})*\].*$
(*) Tag "Firefox:104.x" with ID "f03fd7f9-ea0b-47a9-a0fb-48435d265e8a" has been created
(*) Tag "Firefox:104.x" has been assigned to cli1
~~~

~~~.bash
$ docker run -ti --rm -v "$(pwd)/po2tag:/data:ro" --env-file Docker.env psmiraglia/tenable-helpers po2tag -c 'Firefox' -n '104.x' -f @/data/filters-20811.json --regex '^mozilla firefox.*\[version 104(\.\d{1,})*\].*$'
(*) Filter: {"and": [{"property": "severity", "operator": "eq", "value": [0]}, {"property": "definition.id", "operator": "eq", "value": ["20811"]}]}
(*) Regex: ^mozilla firefox.*\[version 104(\.\d{1,})*\].*$
(*) Tag "Firefox:104.x" with ID "f03fd7f9-ea0b-47a9-a0fb-48435d265e8a" has been created
(*) Tag "Firefox:104.x" has been assigned to cli1
~~~

~~~.bash
$ po2tag -c 'Firefox' -n 'NOT-104.x' -f @po2tag/filters-20811.json --regex @po2tag/regex-20811-firefox-104.txt --regex-negative
(*) Filter: {"and": [{"property": "severity", "operator": "eq", "value": [0]}, {"property": "definition.id", "operator": "eq", "value": ["20811"]}]}
(*) Regex: ^mozilla firefox.*\[version 104(\.\d{1,})*\].*$
(*) Tag "Firefox:104.x" with ID "f03fd7f9-ea0b-47a9-a0fb-48435d265e8a" has been created
(*) Tag "Firefox:104.x" has been assigned to cli12|cli23
~~~

## References

* [pyTenable](https://pytenable.readthedocs.io/en/stable/)
* [Tenable API](https://developer.tenable.com/reference/navigate)

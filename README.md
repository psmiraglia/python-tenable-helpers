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

## agents-info.py

Obtain information about linked agents.

~~~.bash
$ ./agents-info.py -h
usage: agents-info.py [-h] [--never-connect] [--plugins-never-update]
                      [--agent-group-id AGENT_GROUP_ID]

optional arguments:
  -h, --help            show this help message and exit
  --never-connect       list agents that never connected after the linking
  --plugins-never-update
                        list agents that never had pluging update after the
                        linking
  --agent-group-id AGENT_GROUP_ID
                        specify the agent group to get the agents from

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

## References

* [pyTenable](https://pytenable.readthedocs.io/en/stable/)
* [Tenable API](https://developer.tenable.com/reference/navigate)

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

~~~
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

## References

* [pyTenable](https://pytenable.readthedocs.io/en/stable/)
* [Tenable API](https://developer.tenable.com/reference/navigate)

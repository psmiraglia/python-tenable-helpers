# Auto assign network to agents [DRAFT]

The goal is to auto assign network to agents, according to a custom defined logic.

## Extend PyTenable

The script is based on PyTenable but unfortunately, it does not implement [agent bulk operations](https://developer.tenable.com/reference/agent-bulk-operations). Therefore, a new class named `TenableIOExtended` can be created by extending `TenableIO` from PyTenable.

~~~python
from tenable.io import TenableIO
from tenable.io.base import TIOEndpoint


class AgentBulkOperationsAPI(TIOEndpoint):
    def add_to_network(self, network_uuid, items, *args, **kwargs):
        # ref: https://developer.tenable.com/reference/io-agent-bulk-operations-add-to-network
        path = 'scanners/null/agents/_bulk/addToNetwork'
        payload = {'network_uuid': network_uuid, 'items': items}
        self._api.post(path, json=payload)


class TenableIOExtended(TenableIO):
    @property
    def agent_bulk_operations(self):
        return AgentBulkOperationsAPI(self)
~~~

## Implement the custom logic

The logic to detect which network the agent should be member of depends from the final environment.
Therefore, it can be abstracted by defining a function that receives an `agent` object as input and returns the network the agent should be member of.

~~~python
def where_should_it_be(agent, *args, **kwargs):
    network_uuid = ...  # some analysis on agent object
    return network_uuid
~~~

A very simple implementation could be

~~~python
def where_should_it_be(agent, *args, **kwargs):
    network_uuid = ''
    
    # custom defined networks
    networks = {
        'a': 'f3378ff9-86f6-42a9-8bb7-210c01d0ee38',
        'b': 'cbf6a89d-9034-432a-b567-a368bc14a4d5',
        'others': '7012a825-da39-4dc2-9c44-75cb44624fb0'
    }
    
    # the first letter of the agent name
    # is used to identify the network to be assigned
    key = agent.get('name').lower()[0]
    if key in networks:
        network_uuid = networks[key]
    else:
        network_uuid = networks['others']

    return network_uuid
~~~

## Detect agents within `default` network and assign the right one

For each linked agent, the `network_name` attribute is checked. If the value is `default`, the network detection logic is executed.

~~~python
tio = TenableIOExtended(ACCESS_KEY, SECRET_KEY)

result = {}
for agent in tio.agents.list():
    current_network = agent.get('network_name', '')
    if current_network.lower() == 'default':
        net_id = where_should_it_be(agent)
        if net_id:
            a_uuid = agent.get('uuid')
            if net_id not in result:
                result[net_id] = [a_uuid]
            else:
                result[net_id].append(a_uuid)
~~~

Finally, the assignments are applied by invoking a bulk operation.

~~~python
for net_id in result:
    items = result.get(net_id)
    tio.agent_bulk_operations.add_to_network(net_id, items)
~~~


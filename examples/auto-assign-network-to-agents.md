# Auto assign network to agents [DRAFT]

**Goal:** auto assign network according to a custom defined logic

## Detect agents within default network

We scan all the linked agents and if the current network is `default`, we apply the custom logic to assign the correct network

~~~python
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
[...]

for net_id in result:
    items = result.get(net_id)
    tio.agent_bulk_operations.add_to_network(net_id, items)
~~~

## Implement the custom logic

The logic to detect which network the agent should be member of strictly depends on the environment.
Therefore, we confined it in a function that receives an `agent` object as input and returns the uuid of the network the agent should be member of.

~~~python
def where_should_it_be(agent):
    network_uuid = ...  # some analysis on agent object
    return network_uuid
~~~

## Extend PyTenable

PyTenable does not implement agent bulk operations. Therefore, we need to extend it...

~~~python
from tenable.io import TenableIO
from tenable.io.base import TIOEndpoint


class AgentBulkOperationsAPI(TIOEndpoint):
    def add_to_network(self, network_uuid, items, *args, **kwargs):
        path = 'scanners/null/agents/_bulk/addToNetwork'
        payload = {'network_uuid': network_uuid, 'items': items}
        print(json.dumps(payload, indent=2))
        self._api.post(path, json=payload)


class TenableIOExtended(TenableIO):
    @property
    def agent_bulk_operations(self):
        return AgentBulkOperationsAPI(self)


tio = TenableIOExtended(ACCESS_KEY, SECRET_KEY)
~~~

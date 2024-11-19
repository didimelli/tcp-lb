# TCP Load Balancer

The load balancer is implemented in the `lb.py` file.
It exposes two `tcp` servers, one to receive incoming traffic (`recv_server`) and one to handle connections from downstream clients (`lb_server`).

`lb_server` listens for new connections. When a new client is connected, the `lb_handler` keeps the connection up and adds the connection to the list of available downstream connection. When the client disconnects, `lb_handler` removes the connection from the pool of available connections.

`recv_server` listens for incoming traffic. For each message, `recv_handler` randomly chooses a downstream connection and forwards the message to the client.

`processing_client.py` is what is called downstream client above. It connects to the load balancer and processes received messages.
`producer_client.py` just sends data to the load balancer server.

To run this:

```sh
# To run load balancer
uv run lb.py

# To run downstream client. You can run any number of downstream client.
# The more you run, the more parallelization you have.
uv run processing_client.py
uv run processing_client.py

# To send test data to the load balancer
uv run producer_client.py

# You should see data received by the load balancer and then forwarded to each downstream client more or less uniformly.
# You can also see that you can dinamically connect and disconnect downstream clients.
# The load balancer handles that automatically.
```

Currently, as this is just a prototype, the `lock` and the connection pool are simply global variables.

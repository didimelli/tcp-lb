import random
from typing import List

from anyio import TASK_STATUS_IGNORED, Lock, create_task_group, create_tcp_listener, run
from anyio.abc import SocketStream, TaskStatus

# Pool of downstream connections
STREAMS: List[SocketStream] = []
# Lock to sync access to the pool
LOCK = Lock()


async def recv_handler(stream: SocketStream) -> None:
    """
    Handler for incoming data. Forwards each message to a random available
    connection in the pool.
    """
    async with stream:
        async for raw in stream:
            msg = raw.decode()
            print("Received message", msg)
            async with LOCK:
                if not STREAMS:
                    print("Dropping packet", msg, "because no-one is listening.")
                    continue
                await random.choice(STREAMS).send(msg.encode())


async def recv_server() -> None:
    """Exposes a tcp server for incoming data."""
    async with await create_tcp_listener(local_port=12345) as listener:
        await listener.serve(recv_handler)


async def lb_handler(stream: SocketStream) -> None:
    """
    Keep alive each new connection and adds it to the pool.
    When the client is disconnected, remove the connection from the pool.
    """
    print(
        "Got new connection",
    )
    try:
        async with stream:
            async with LOCK:
                print("Adding connection to pool.")
                # Add the connection to the pool
                STREAMS.append(stream)
            async for _ in stream:
                # Keep the connection alive
                pass
    finally:
        async with LOCK:
            print("Removing connection from pool.")
            # When the client is disconnected, remove the connection from the pool
            STREAMS.remove(stream)


async def lb_server(
    *,
    task_status: TaskStatus[None] = TASK_STATUS_IGNORED,
) -> None:
    """
    Listens for incoming connections from downstream clients.
    """
    async with await create_tcp_listener(local_port=12346) as listener:
        task_status.started()
        await listener.serve(lb_handler)


async def main() -> None:
    """
    Starts both the `recv_server` and the `lb_server` concurrently.
    """
    async with create_task_group() as tg:
        await tg.start(lb_server)
        tg.start_soon(recv_server)


if __name__ == "__main__":
    run(main)

import random
from typing import List

from anyio import TASK_STATUS_IGNORED, Lock, create_task_group, create_tcp_listener, run
from anyio.abc import SocketStream, TaskStatus

STREAMS: List[SocketStream] = []
LOCK = Lock()


async def recv_handler(stream: SocketStream) -> None:
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
    async with await create_tcp_listener(local_port=12345) as listener:
        await listener.serve(recv_handler)


async def lb_handler(stream: SocketStream) -> None:
    print(
        "Got new connection",
    )
    try:
        async with stream:
            async with LOCK:
                print("Adding connection to pool.")
                STREAMS.append(stream)
            # await stream.send(msg.encode())
            async for _ in stream:
                pass
    finally:
        async with LOCK:
            print("Removing connection from pool.")
            STREAMS.remove(stream)


async def lb_server(
    *,
    task_status: TaskStatus[None] = TASK_STATUS_IGNORED,
) -> None:
    # listen for incoming connections and store them in state
    async with await create_tcp_listener(local_port=12346) as listener:
        task_status.started()
        await listener.serve(lb_handler)


async def main() -> None:
    async with create_task_group() as tg:
        await tg.start(lb_server)
        tg.start_soon(recv_server)


if __name__ == "__main__":
    run(main)

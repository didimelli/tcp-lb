from anyio import connect_tcp, run


async def main() -> None:
    async with await connect_tcp("127.0.0.1", 12346) as tcp:
        while True:
            msg = (await tcp.receive(10)).decode()
            print("Processing message", msg)


if __name__ == "__main__":
    run(main)

from anyio import connect_tcp, run, sleep


async def main() -> None:
    i = 0
    async with await connect_tcp("127.0.0.1", 12345) as tcp:
        while True:
            msg = str(i) + "abcdefghil"[len(str(i)) :]
            await tcp.send(msg.encode())
            await sleep(0.1)
            i += 1


if __name__ == "__main__":
    run(main)

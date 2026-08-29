import time

from VoltaLibPython import VoltaClient

def main():
    client = VoltaClient()
    while True:
        client.test()
        client._print_remaning_time()
        for remaining in range(60, 0, -1):
            print(f"Refreshing in {remaining} seconds", end="\r", flush=True)
            time.sleep(1)
        print(" " * 40, end="\r", flush=True)

main()
import json
import os

from VoltaLibPython import VoltaClient

def main():
    with VoltaClient() as client:
        client.get.library.tracks()

        with open("tracks.json", "w") as f:
            json.dump(client.get.library.tracks(), f, indent=4)

def pause():
    input("Press Enter to exit and clear...")
    clear()

def clear():
    for filename in os.listdir("."):
        if filename.endswith(".json"):
            os.remove(filename)

main()
pause()
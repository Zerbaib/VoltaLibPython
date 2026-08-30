import json
import os

from VoltaLibPython import VoltaClient

def main():
    with VoltaClient() as client:
        print("Starting test")
        var = client.get.library.playlists(id="3f5d2513-1170-4922-b980-1df9a4ad158c")
        print("Variable was fetched, saving to temp.json")

        with open("temp.json", "w") as f:
            json.dump(var, f, indent=4)

def pause():
    input("Press Enter to exit and clear...")
    clear()
def clear():
    for filename in os.listdir("."):
        if filename.endswith(".json"):
            os.remove(filename)

main()
pause()
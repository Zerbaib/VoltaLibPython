import json
import os

from VoltaLibPython import VoltaClient

def main():
    with VoltaClient() as client:
        print("Starting test")
        var = client.get.catalog.search("Tetoris")
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
import json

from VoltaLibPython import VoltaClient

def main():
    with VoltaClient() as client:
        #tracks = client.get.library.tracks()
        #albums = client.get.library.albums()
        #artists = client.get.library.artists()
        #artists_albums = client.get.library.artist_albums("m")
        #artists_tracks = client.get.library.artist_tracks("m")
        #playlists = client.get.library.playlists()
        playlists_id = client.get.library.playlists("3d4aefb7-0a8b-43ac-9f91-6fc4f1dbb62f")

        with open("temp.json", "w", encoding="utf-8") as f:
                    json.dump(playlists_id, f, indent=4)
        pass

main()
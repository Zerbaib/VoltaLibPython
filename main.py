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
        #playlists_tracks = client.get.library.playlist_tracks("3d4aefb7-0a8b-43ac-9f91-6fc4f1dbb62f")
        
        client.post.track({
            "id": "11111111-1111-1111-1111-111111111111",
            "name": "Test Track",
            "artist": "Test Artist",
            "album": "Test Album",
            "duration": 180,
        })

        pass

main()
import time

from VoltaLibPython import VoltaClient, client

def test_timing_refresh():
    client = VoltaClient()
    while True:
        client.test()
        client._print_remaning_time()
        for remaining in range(60, 0, -1):
            print(f"Refreshing in {remaining} seconds", end="\r", flush=True)
            time.sleep(1)
        print(" " * 40, end="\r", flush=True)

def main():
    with VoltaClient() as client:
        tracks = client.get.library.tracks()
        albums = client.get.library.albums()
        artists = client.get.library.artists()
        artists_albums = client.get.library.artist_albums("artist_id")
        artists_tracks = client.get.library.artist_tracks("artist_id")
        playlists = client.get.library.playlists()
        playlists_id = client.get.library.playlists("playlist_id")

main()
from VoltaLibPython import VoltaClient

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
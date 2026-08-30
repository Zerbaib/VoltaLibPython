# How to use

## Config

in `.env` file:
```
CLIENT_ID=volta_id_XXXXXXXXXXXXXXXXXX
CLIENT_SECRET=volta_sk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```


## In your project
```python
from VoltaLibPython import VoltaClient

client = VoltaClient()
```

# Documentations
## GET

```python
def main():
	with VoltaClient() as client:
		tracks = client.get.library.tracks()                           # Fetch all liked song
		albums = client.get.library.albums()                           # Fetch all your albums
		artists = client.get.library.artists()                         # Fetch all artists followed
		artists_albums = client.get.library.artist_albums("artist_id") # Fetch all album from one artist
		artists_tracks = client.get.library.artist_tracks("artist_id") # Fetch all song from one artist
		playlists = client.get.library.playlists()                     # Fetch all your playlist
		playlists_id = client.get.library.playlists("playlist_id")     # Fetch all info of one playlist

```


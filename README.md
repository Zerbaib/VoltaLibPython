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
		var = client.get.library.tracks() # Change tracks with good function

```

| Function                                      | Utility                         | Output                                                                                                                                                                                                                                               |
| --------------------------------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| client.get.library.tracks()                   | Fetch all liked song            | \[{"id": "id",<br>"title": "title",<br>"artist": "artist",<br>"artist_id": "artistid",<br>"album": "album",<br>"album_id": "albumid",<br>"cover_url": "url",<br>"duration_ms": 000000,<br>"added_at": "timestamp",<br>"in_library": true/false<br>}] |
| client.get.library.albums()                   | Fetch all your albums           | \[{"id": "id",<br>"title": "title",<br>"artist": "artist",<br>"cover_url": "url",<br>"release_date": "01/01/2026",<br>"track_count": 1<br>}]                                                                                                         |
| client.get.library.artists()                  | Fetch all artists followed      |                                                                                                                                                                                                                                                      |
| client.get.library.artist_albums("artist_id") | Fetch all album from one artist |                                                                                                                                                                                                                                                      |
| client.get.library.artist_tracks("artist_id") | Fetch all song from one artist  |                                                                                                                                                                                                                                                      |
| client.get.library.playlists()                | Fetch all your playlist         |                                                                                                                                                                                                                                                      |
| client.get.library.playlists("playlist_id")   | Fetch all info of one playlist  |      
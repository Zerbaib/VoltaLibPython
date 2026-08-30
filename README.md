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

| Function                                      | Utility                         | Output                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| --------------------------------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| client.get.library.tracks()                   | Fetch all liked song            | [{"id": "id",<br>"title": "title",<br>"artist": "artist",<br>"artist_id": "artistid",<br>"album": "album",<br>"album_id": "albumid",<br>"cover_url": "url",<br>"duration_ms": 000000,<br>"added_at": "timestamp",<br>"in_library": true/false}]                                                                                                                                                                                                                 |
| client.get.library.albums()                   | Fetch all your albums           | [{"id": "id",<br>"title": "title",<br>"artist": "artist",<br>"cover_url": "url",<br>"release_date": "01/01/2026",<br>"track_count": 1}]                                                                                                                                                                                                                                                                                                                         |
| client.get.library.artists()                  | Fetch all artists followed      | [{"id": "id",<br>"name": "name",<br>"picture_url": "url",<br>"album_count": 1,<br>"track_count": 1}]                                                                                                                                                                                                                                                                                                                                                            |
| client.get.library.artist_albums("artist_id") | Fetch all album from one artist | [{"id": "id",<br>"title": "title",<br>"artist": "artist",<br>"cover_url": "url",<br>"release_date": "01/01/2026",<br>"track_count": 1}]                                                                                                                                                                                                                                                                                                                         |
| client.get.library.artist_tracks("artist_id") | Fetch all song from one artist  | [{"id": "id",<br>"title": "title",<br>"artist": "artist0,artist1",<br>"artist_id": "artistid",<br>"album": "album",<br>"album_id": "albumid",<br>"cover_url": "url",<br>"duration_ms": 00000,<br>"added_at": "timestamp"}]                                                                                                                                                                                                                                      |
| client.get.library.playlists()                | Fetch all your playlist         | [{<br>"id": "id",<br>"name": "name",<br>"user_id": "userid",<br>"description": "description",<br>"cover_url": "url",<br>"is_public": 0/1,<br>"created_at": "timestamp",<br>"updated_at": "timestamp",<br>"track_count": 1,<br>"total_duration_ms": 0000<br>}]                                                                                                                                                                                                   |
| client.get.library.playlists("playlist_id")   | Fetch all info of one playlist  | {"id": "id",<br>"name": "name",<br>"description": "description",<br>"user_id": "userid",<br>"cover_url": "url",<br>"is_public": 0/1,<br>"is_owner": true/false,<br>"can_edit": true/false,<br>"tracks": [{<br>"id": "id",<br>"title": "title",<br>"artist": "artist",<br>"artist_id": "artistid",<br>"album": "album",<br>"album_id": "albumid",<br>"cover_url": "url",<br>"duration_ms": 0000,<br>"added_at": "timestamp",<br>"playlist_track_id": "id"<br>}]} |
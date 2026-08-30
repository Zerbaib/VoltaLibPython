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
client.GET().Library().tracks()                # Fetch all liked song
client.GET().Library().albums()                # Fetch all your albums
client.GET().Library().artists()               # Fetch all artists followed
client.GET().Library().artist_albums(id="str") # Fetch all album from one artist
client.GET().Library().artist_tracks(id="str") # Fetch all song from one artist
client.GET().Library().playlists()             # Fetch all your playlist
client.GET().Library().playlists(id="str")     # Fetch all info of one playlist
```


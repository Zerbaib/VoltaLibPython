# GET method
# Tables
* In your library
  * [tracks()](#tracks)
  * [albums()](#albums)
  * [artists()](#artists)


## GET in your library

Fetch many data in your library, 
you cannot use this for a global use or search.



### tracks()
> Get all liked tracks.
>
> If a search string is provided, filter the tracks by title containing the search string (case-insensitive).
>
> Args:
> - search (str, optional): A string to filter tracks by title. Defaults to None.

#### Use:
```python
with VoltaClient() as client:
    client.get.library.tracks()             # Fetch all liked song
    client.git.library.tracks("Song Title") # Search all match with the title in your liked song
```



### albums()
> Get all liked albums.
>
> If a search string is provided, filter the albums by title containing the search string (case-insensitive).
>
> Args:
> - search (str, optional): A string to filter albums by title. Defaults to None.

#### Use:
```python
with VoltaClient() as client:
    client.get.library.albums()              # Fetch all album in your liked song
    client.git.library.tracks("Album Title") # Search all match with the title album in your liked song
```



### artists()
> Get all liked artists.
>
> If a search string is provided, filter the artists by name containing the search string (case-insensitive).
>
> Args:
> - search (str, optional): A string to filter artists by name. Defaults to None.

#### Use:
```python
with VoltaClient() as client:
    client.get.library.artists()             # Fetch all artists followed
    client.git.library.tracks("Artist name") # Search all match with the artists name in your followed
```



### Soon ..
#### I need to finish the doc
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
		var = client.get.library.tracks()

```

### Find all get function [here](./docs/GET.md)

---


## POST

```python
def main():
	with VoltaClient() as client:
		var = client.post.library.tracks()

```
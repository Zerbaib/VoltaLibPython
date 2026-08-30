"""
Tests pour les requêtes POST, PUT et DELETE de VoltaClient.

Lancer avec : pytest tests/test_post_put_delete.py -v

Note : `VoltaClient` n'expose pas encore de méthode PUT à ce jour (seuls
GET, POST et DELETE existent dans client.py). La classe `TestPut`
ci-dessous est laissée en placeholder — dès que `client.put` sera ajouté
(sur le modèle de `_delete`, avec refresh automatique sur 401), il suffira
de remplir cette classe avec les mêmes scénarios que `TestPost`/`TestDelete`
ci-dessous (succès, 401 avec retry, non-200 qui lève `APIError`).
"""

from __future__ import annotations

import pytest

from VoltaLibPython.exceptions import APIError

from .conftest import FakeResponse


# ---------------------------------------------------------------------------
# POST
# ---------------------------------------------------------------------------

class TestPost:
    def test_post_track_success(self, make_client, fake_session):
        client = make_client()
        fake_session.post_responses.append(FakeResponse(200, {"id": "t1"}))

        result = client.post.track({"track_id": "t1"})

        assert result == {"id": "t1"}
        method, url, headers, payload = fake_session.calls[0]
        assert method == "POST"
        assert url.endswith("/api/v1/library/tracks")
        assert payload == {"track_id": "t1"}
        assert headers["Authorization"] == "Bearer initial_token"

    def test_post_401_refreshes_and_retries(self, make_client, fake_session):
        client = make_client({"access_token": "old_token", "expires_in": 3600})

        fake_session.post_responses.append(FakeResponse(401, text="invalid"))
        fake_session.post_responses.append(
            FakeResponse(200, {"access_token": "new_token", "expires_in": 3600})
        )
        fake_session.post_responses.append(FakeResponse(200, {"id": "t1"}))

        result = client.post.track({"track_id": "t1"})

        assert result == {"id": "t1"}
        assert client.token == "new_token"

    def test_post_non_200_raises_api_error(self, make_client, fake_session):
        client = make_client()
        fake_session.post_responses.append(FakeResponse(400, text="bad request"))

        with pytest.raises(APIError):
            client.post.track({"track_id": "t1"})

    def test_post_request_generic_endpoint(self, make_client, fake_session):
        client = make_client()
        fake_session.post_responses.append(FakeResponse(200, {"ok": True}))

        result = client.post.request("/api/v1/library/playlists", {"name": "Roadtrip"})

        assert result == {"ok": True}
        _, url, _, payload = fake_session.calls[0]
        assert url.endswith("/api/v1/library/playlists")
        assert payload == {"name": "Roadtrip"}


# ---------------------------------------------------------------------------
# PUT — pas encore implémenté côté client, tests à écrire dès que ça l'est.
# ---------------------------------------------------------------------------

class TestPut:
    @pytest.mark.skip(reason="PUT not supported by FakeSession yet")
    def test_put_reorder_playlist_tracks_success(self, make_client, fake_session):
        client = make_client()
        result = client.put.request(
            "/api/v1/library/playlists/pl1/tracks",
            {"track_ids": ["t2", "t1"]},
        )
        assert result == {"ok": True}

    @pytest.mark.skip(reason="PUT not supported by FakeSession yet")
    def test_put_401_refreshes_and_retries(self, make_client, fake_session):
        client = make_client({"access_token": "old_token", "expires_in": 3600})
        result = client.put.request("/api/v1/library/playlists/pl1/tracks", {"track_ids": []})
        assert result == {"ok": True}

    @pytest.mark.skip(reason="PUT not supported by FakeSession yet")
    def test_put_non_200_raises_api_error(self, make_client, fake_session):
        client = make_client()
        with pytest.raises(APIError):
            client.put.request("/api/v1/library/playlists/pl1/tracks", {"track_ids": []})


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

class TestDelete:
    def test_delete_track_success(self, make_client, fake_session):
        client = make_client()
        fake_session.delete_responses.append(FakeResponse(200, {"deleted": True}))

        result = client.delete.track("t1")

        assert result == {"deleted": True}
        method, url, headers, _ = fake_session.calls[0]
        assert method == "DELETE"
        assert url.endswith("/api/v1/library/tracks/t1")
        assert headers["Authorization"] == "Bearer initial_token"

    def test_delete_401_refreshes_and_retries(self, make_client, fake_session):
        client = make_client({"access_token": "old_token", "expires_in": 3600})

        fake_session.delete_responses.append(FakeResponse(401, text="invalid"))
        fake_session.post_responses.append(
            FakeResponse(200, {"access_token": "new_token", "expires_in": 3600})
        )
        fake_session.delete_responses.append(FakeResponse(200, {"deleted": True}))

        result = client.delete.track("t1")

        assert result == {"deleted": True}
        assert client.token == "new_token"

    def test_delete_non_200_raises_api_error(self, make_client, fake_session):
        client = make_client()
        fake_session.delete_responses.append(FakeResponse(404, text="not found"))

        with pytest.raises(APIError):
            client.delete.track("unknown_id")

    def test_delete_request_sends_body(self, make_client, fake_session):
        client = make_client()
        fake_session.delete_responses.append(FakeResponse(200, {"ok": True}))

        client.delete.request("/api/v1/library/playlists/pl1/tracks/t1", {"reason": "cleanup"})

        _, _, _, payload = fake_session.calls[0]
        assert payload == {"reason": "cleanup"}
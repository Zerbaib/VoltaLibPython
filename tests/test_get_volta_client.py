"""
Tests pour les requêtes GET de VoltaClient.

Lancer avec : pytest tests/test_get.py -v
"""

from __future__ import annotations

import pytest

from VoltaLibPython.exceptions import APIError

from .conftest import FakeResponse


class TestGet:
    def test_get_success_returns_json(self, make_client, fake_session):
        client = make_client()
        fake_session.get_responses.append(FakeResponse(200, {"tracks": ["a", "b"]}))

        result = client.get.library.tracks()

        assert result == {"tracks": ["a", "b"]}
        method, url, headers, params = fake_session.calls[0]
        assert method == "GET"
        assert url == f"{client.base_url}/api/v1/library/tracks"
        assert headers["Authorization"] == "Bearer initial_token"

    def test_get_non_200_raises_api_error(self, make_client, fake_session):
        client = make_client()
        fake_session.get_responses.append(
            FakeResponse(500, text="internal error")
        )

        with pytest.raises(APIError):
            client.get.library.tracks()

    def test_get_401_refreshes_token_and_retries_transparently(
        self, make_client, fake_session
    ):
        client = make_client({"access_token": "old_token", "expires_in": 3600})

        # 1er appel : jeton refusé
        fake_session.get_responses.append(
            FakeResponse(401, text='{"detail":"Invalid token"}')
        )
        # refresh de token déclenché en interne
        fake_session.post_responses.append(
            FakeResponse(200, {"access_token": "new_token", "expires_in": 3600})
        )
        # 2e appel (après refresh) : succès
        fake_session.get_responses.append(FakeResponse(200, {"tracks": []}))

        result = client.get.library.tracks()  # ne doit lever aucune exception

        assert result == {"tracks": []}
        assert client.token == "new_token"

        get_calls = [c for c in fake_session.calls if c[0] == "GET"]
        assert len(get_calls) == 2
        assert get_calls[0][2]["Authorization"] == "Bearer old_token"
        assert get_calls[1][2]["Authorization"] == "Bearer new_token"

    def test_get_401_twice_raises_after_single_retry(self, make_client, fake_session):
        client = make_client({"access_token": "old_token", "expires_in": 3600})

        # Le jeton reste invalide même après refresh (ex: clé révoquée).
        fake_session.get_responses.append(FakeResponse(401, text="invalid"))
        fake_session.post_responses.append(
            FakeResponse(200, {"access_token": "new_token", "expires_in": 3600})
        )
        fake_session.get_responses.append(FakeResponse(401, text="invalid"))

        with pytest.raises(APIError):
            client.get.library.tracks()

        # Une seule tentative de refresh, une seule retentative de la requête.
        get_calls = [c for c in fake_session.calls if c[0] == "GET"]
        assert len(get_calls) == 2

    def test_playlists_without_id_lists_all(self, make_client, fake_session):
        client = make_client()
        fake_session.get_responses.append(FakeResponse(200, {"playlists": []}))

        client.get.library.playlists()

        _, url, _, _ = fake_session.calls[0]
        assert url.endswith("/api/v1/library/playlists")

    def test_playlists_with_id_gets_single_playlist(self, make_client, fake_session):
        client = make_client()
        fake_session.get_responses.append(FakeResponse(200, {"id": "pl_123"}))

        client.get.library.playlists(id="pl_123")

        _, url, _, _ = fake_session.calls[0]
        assert url.endswith("/api/v1/library/playlists/pl_123")

    @pytest.mark.parametrize(
        "method_name, args, expected_suffix",
        [
            ("tracks", (), "/tracks"),
            ("albums", (), "/albums"),
            ("artists", (), "/artists"),
            ("artist_albums", ("artist_1",), "/artists/artist_1/albums"),
            ("artist_tracks", ("artist_1",), "/artists/artist_1/tracks"),
        ],
    )
    def test_library_get_endpoints_hit_expected_url(
        self, make_client, fake_session, method_name, args, expected_suffix
    ):
        client = make_client()
        fake_session.get_responses.append(FakeResponse(200, {}))

        getattr(client.get.library, method_name)(*args)

        _, url, _, _ = fake_session.calls[0]
        assert url.endswith(f"/api/v1/library{expected_suffix}")
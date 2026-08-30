"""
Tests pour VoltaClient.

Lancer avec : pytest tests/ -v
"""

from __future__ import annotations

import json
import time

import pytest

from VoltaLibPython.exceptions import APIError
from VoltaLibPython.client import VoltaClient

from .conftest import FakeResponse


# ---------------------------------------------------------------------------
# Chargement / sauvegarde du token
# ---------------------------------------------------------------------------

class TestTokenLoading:
    def test_load_token_reads_existing_file_without_network_call(
        self, tmp_path, monkeypatch, fake_session
    ):
        token_file = tmp_path / "token.json"
        token_file.write_text(json.dumps({"access_token": "from_disk", "expires_in": 1200}))

        client = VoltaClient(token_file=str(token_file))
        client._session = fake_session
        try:
            assert client.token == "from_disk"
            assert client.refresh_interval == 1200
            # Aucun appel réseau n'a dû être fait pour charger un token déjà présent.
            assert fake_session.calls == []
        finally:
            client.stop_background_refresh()

    def test_load_token_triggers_refresh_when_file_missing(self, tmp_path, monkeypatch):
        token_file = tmp_path / "does_not_exist" / "token.json"

        # On patche _build_session pour injecter notre fausse session AVANT
        # que __init__ ne s'en serve pour aller chercher le premier token.
        from tests.conftest import FakeSession

        session = FakeSession()
        session.post_responses.append(
            FakeResponse(200, {"access_token": "brand_new", "expires_in": 3600})
        )
        monkeypatch.setattr("VoltaLibPython.client._build_session", lambda: session)

        client = VoltaClient(token_file=str(token_file))
        try:
            assert client.token == "brand_new"
            assert token_file.exists()  # le token obtenu a bien été persisté
            saved = json.loads(token_file.read_text())
            assert saved["access_token"] == "brand_new"
        finally:
            client.stop_background_refresh()


class TestSaveRemainingTime:
    def test_stop_background_refresh_saves_remaining_time(self, make_client, tmp_path):
        client = make_client({"access_token": "tok", "expires_in": 3600})
        token_file = tmp_path / "token.json"

        client.stop_background_refresh()

        saved = json.loads(token_file.read_text())
        # Quelques millisecondes se sont écoulées entre la création et l'arrêt :
        # on attend une valeur légèrement inférieure à 3600, jamais négative.
        assert 3590 <= saved["expires_in"] <= 3600

    def test_stop_background_refresh_is_idempotent(self, make_client):
        client = make_client()
        client.stop_background_refresh()
        # Un second appel ne doit ni lever d'exception ni re-sauvegarder.
        client.stop_background_refresh()  # ne doit pas planter

    def test_context_manager_stops_refresh_and_closes_session(
        self, tmp_path, monkeypatch, fake_session
    ):
        token_data = {"access_token": "tok", "expires_in": 3600}
        monkeypatch.setattr(VoltaClient, "_load_token", lambda self: dict(token_data))

        with VoltaClient(token_file=str(tmp_path / "token.json")) as client:
            client._session = fake_session
            assert client._closed is False

        assert client._closed is True
        assert fake_session.closed is True


# ---------------------------------------------------------------------------
# GET
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Thread-safety légère du token
# ---------------------------------------------------------------------------

class TestTokenThreadSafety:
    def test_auth_headers_reflects_token_after_manual_refresh(self, make_client, fake_session):
        client = make_client({"access_token": "old_token", "expires_in": 3600})
        assert client._auth_headers()["Authorization"] == "Bearer old_token"

        fake_session.post_responses.append(
            FakeResponse(200, {"access_token": "manually_refreshed", "expires_in": 3600})
        )
        client._handle_unauthorized()

        assert client._auth_headers()["Authorization"] == "Bearer manually_refreshed"
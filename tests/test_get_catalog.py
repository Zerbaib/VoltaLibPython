"""
Tests pour client.get.catalog.

Lancer avec : pytest tests/test_get_catalog.py -v
"""

from __future__ import annotations

import pytest

from VoltaLibPython.exceptions import APIError

from .conftest import FakeResponse


class TestCatalogSearch:
    def test_search_success_returns_json(self, make_client, fake_session):
        client = make_client()
        fake_session.get_responses.append(
            FakeResponse(200, {"tracks": [], "artists": [], "albums": [], "playlists": []})
        )

        result = client.get.catalog.search("daft punk")

        assert result == {"tracks": [], "artists": [], "albums": [], "playlists": []}

    def test_search_builds_expected_url(self, make_client, fake_session):
        client = make_client()
        fake_session.get_responses.append(FakeResponse(200, {}))

        client.get.catalog.search("daft punk")

        _, url, _, params = fake_session.calls[0]
        assert url.endswith("/api/v1/search?q=daft punk")
        # Le paramètre q est concaténé directement dans l'endpoint plutôt que
        # passé via `params=`, donc aucun `params` n'est transmis à la session.
        assert params is None

    def test_search_query_is_not_url_encoded(self, make_client, fake_session):
        """Comportement actuel documenté : `query` est inséré tel quel dans
        l'URL (`f"{endpoint}/search?q={query}"`) sans passer par
        `urllib.parse.quote` ni par le paramètre `params=` de requests, qui
        s'en chargerait automatiquement. Une requête contenant des espaces ou
        des caractères spéciaux (`&`, `#`, `=`, accents...) part donc non
        encodée. Ça fonctionne pour un mot simple mais peut casser l'appel
        réel à l'API pour des requêtes plus complexes — à corriger en passant
        par `params={"q": query}` si besoin."""
        client = make_client()
        fake_session.get_responses.append(FakeResponse(200, {}))

        client.get.catalog.search("daft & punk")

        _, url, _, _ = fake_session.calls[0]
        assert url.endswith("/api/v1/search?q=daft & punk")  # espace/& non encodés

    def test_search_non_200_raises_api_error(self, make_client, fake_session):
        client = make_client()
        fake_session.get_responses.append(FakeResponse(500, text="internal error"))

        with pytest.raises(APIError):
            client.get.catalog.search("daft punk")

    def test_search_401_refreshes_token_and_retries_transparently(
        self, make_client, fake_session
    ):
        client = make_client({"access_token": "old_token", "expires_in": 3600})

        fake_session.get_responses.append(FakeResponse(401, text="invalid"))
        fake_session.post_responses.append(
            FakeResponse(200, {"access_token": "new_token", "expires_in": 3600})
        )
        fake_session.get_responses.append(FakeResponse(200, {"tracks": []}))

        result = client.get.catalog.search("daft punk")

        assert result == {"tracks": []}
        assert client.token == "new_token"
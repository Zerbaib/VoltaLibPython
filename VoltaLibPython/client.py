from __future__ import annotations

import atexit
import json
import logging
import os
import threading
import time
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

from .exceptions import APIError

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 20
TOKEN_REFRESH_MARGIN = 30


def _build_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=("GET", "POST"),
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class VoltaClient:
    def __init__(
        self,
        base_url: str = "https://api.volta-music.com",
        token_file: str = "config/token.json",
    ) -> None:
        self.token_file = token_file
        self.base_url = base_url
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")

        self._session = _build_session()
        self._token_lock = threading.Lock()
        self._refresh_timer: Optional[threading.Timer] = None
        self._closed = False

        self.token_data: dict[str, Any] = self._load_token()
        self.token: Optional[str] = self.token_data.get("access_token")
        self.refresh_interval: int = int(self.token_data.get("expires_in", 3600))

        self._start_background_refresh()

        # Sous-espaces de l'API, liés à cette instance (pas de nouveau
        # VoltaClient créé à chaque accès).
        self.get = self._GET(self)
        self.post = self._POST(self)
        self.delete = self._DELETE(self)

    # -- Gestion du token -------------------------------------------------

    def _refresh_token(self) -> dict[str, Any]:
        url = f"{self.base_url}/api/v1/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = self._session.post(url, data=payload, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise APIError(
                f"Failed to refresh token: {response.status_code} - {response.text}"
            )
        token_data = response.json()
        self._save_token(token_data)
        return token_data

    def _save_token(self, token_data: dict[str, Any]) -> None:
        directory = os.path.dirname(self.token_file)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(self.token_file, "w") as f:
            json.dump(token_data, f, indent=4)

    def _load_token(self) -> dict[str, Any]:
        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as f:
                return json.load(f)
        return self._refresh_token()

    def _start_background_refresh(self) -> None:
        if self._refresh_timer is not None:
            self._refresh_timer.cancel()
        delay = max(self.refresh_interval - TOKEN_REFRESH_MARGIN, 1)
        self._expiry_deadline = time.monotonic() + self.refresh_interval
        self._refresh_timer = threading.Timer(delay, self._background_refresh_tick)
        self._refresh_timer.daemon = True
        self._refresh_timer.start()

    def _remaining_seconds(self) -> int:
        """Temps restant (en secondes) avant l'expiration réelle du token,
        calculé à partir d'une horloge monotone (insensible aux changements
        d'heure système)."""
        return max(int(self._expiry_deadline - time.monotonic()), 0)

    def _save_remaining_time(self) -> None:
        """Met à jour `expires_in` dans le fichier de token avec le temps
        restant réel, plutôt que la valeur d'origine renvoyée par l'API.
        Appelé à l'arrêt du thread de fond (fin de programme, sortie du
        context manager, ou arrêt manuel)."""
        try:
            with self._token_lock:
                remaining = self._remaining_seconds()
                self.token_data["expires_in"] = remaining
                token_data_copy = dict(self.token_data)
            self._save_token(token_data_copy)
        except Exception:
            logger.exception("Impossible de sauvegarder le temps restant du token")

    def _background_refresh_tick(self) -> None:
        try:
            token_data = self._refresh_token()
            with self._token_lock:
                self.token_data = token_data
                self.token = token_data.get("access_token")
                self.refresh_interval = int(token_data.get("expires_in", 3600))
        except Exception:
            logger.exception("Token refresh failed; retrying in 30s")
            self.refresh_interval = 30
        if not self._closed:
            self._start_background_refresh()

    def stop_background_refresh(self) -> None:
        if self._closed:
            return  # déjà arrêté (évite une double sauvegarde via atexit + __exit__)
        self._closed = True
        if self._refresh_timer is not None:
            self._refresh_timer.cancel()
            self._refresh_timer = None
        self._save_remaining_time()

    def __enter__(self) -> "VoltaClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.stop_background_refresh()
        self._session.close()

    def _auth_headers(self) -> dict[str, str]:
        with self._token_lock:
            token = self.token
        return {"Authorization": f"Bearer {token}"}

    # -- Rafraîchissement suite à un 401 ------------------------------------

    def _handle_unauthorized(self) -> None:
        """Force un nouveau jeton suite à un 401 (jeton invalide/expiré côté
        serveur avant même notre propre échéance de refresh), de façon
        thread-safe, et reprogramme le refresh automatique sur la nouvelle
        échéance."""
        logger.info("401 reçu : jeton invalide, rafraîchissement forcé.")
        token_data = self._refresh_token()
        with self._token_lock:
            self.token_data = token_data
            self.token = token_data.get("access_token")
            self.refresh_interval = int(token_data.get("expires_in", 3600))
        self._start_background_refresh()

    # -- Requêtes de base ---------------------------------------------------

    def _get(
        self, endpoint: str, params: Optional[dict[str, Any]] = None, _retry: bool = True
    ) -> Any:
        url = f"{self.base_url}{endpoint}"
        response = self._session.get(
            url, headers=self._auth_headers(), params=params, timeout=DEFAULT_TIMEOUT
        )
        if response.status_code == 401 and _retry:
            self._handle_unauthorized()
            return self._get(endpoint, params, _retry=False)
        if response.status_code != 200:
            raise APIError(f"GET request failed: {response.status_code} - {response.text}")
        return response.json()

    def _post(
        self, endpoint: str, data: dict[str, Any], _retry: bool = True
    ) -> Any:
        url = f"{self.base_url}{endpoint}"
        response = self._session.post(
            url, headers=self._auth_headers(), json=data, timeout=DEFAULT_TIMEOUT
        )
        if response.status_code == 401 and _retry:
            self._handle_unauthorized()
            return self._post(endpoint, data, _retry=False)
        if response.status_code != 200:
            raise APIError(f"POST request failed: {response.status_code} - {response.text}")
        return response.json()

    def _delete(self, endpoint: str, _retry: bool = True) -> Any:
        url = f"{self.base_url}{endpoint}"
        response = self._session.delete(
            url, headers=self._auth_headers(), timeout=DEFAULT_TIMEOUT
        )
        if response.status_code == 401 and _retry:
            self._handle_unauthorized()
            return self._delete(endpoint, _retry=False)
        if response.status_code != 200:
            raise APIError(f"DELETE request failed: {response.status_code} - {response.text}")
        return response.json()

    # -- Sous-espaces ---------------------------------------------------

    class _GET:
        """Espace de noms pour les requêtes GET. Utilise le client parent,
        ne crée jamais de nouvelle instance de VoltaClient."""

        def __init__(self, client: "VoltaClient") -> None:
            self.client = client
            self.library = VoltaClient._Library(client)

        def request(self, endpoint: str) -> Any:
            return self.client._get(endpoint)

    class _POST:
        def __init__(self, client: "VoltaClient") -> None:
            self.client = client

        def request(self, endpoint: str, data: dict[str, Any]) -> Any:
            return self.client._post(endpoint, data)

        def track(self, data: dict[str, Any]) -> Any:
            return self.client._post("/api/v1/library/tracks", data)

    class _DELETE:
        def __init__(self, client: "VoltaClient") -> None:
            self.client = client

        def request(self, endpoint: str, data: dict[str, Any]) -> Any:
            return self.client._delete(endpoint, data)

        def track(self, track_id: str) -> Any:
            return self.client._delete(f"/api/v1/library/tracks/{track_id}")
        

    class _Library:
        def __init__(self, client: "VoltaClient") -> None:
            self.client = client
            self.endpoint = "/api/v1/library"
        def tracks(self) -> Any:
            return self.client._get(f"{self.endpoint}/tracks")
        def albums(self) -> Any:
            return self.client._get(f"{self.endpoint}/albums")
        def artists(self) -> Any:
            return self.client._get(f"{self.endpoint}/artists")
        def artist_albums(self, id: str) -> Any:
            return self.client._get(f"{self.endpoint}/artists/{id}/albums")
        def artist_tracks(self, id: str) -> Any:
            return self.client._get(f"{self.endpoint}/artists/{id}/tracks")
        def playlists(self, id: str = None) -> Any:
            if id:
                return self.client._get(f"{self.endpoint}/playlists/{id}")
            else:
                return self.client._get(f"{self.endpoint}/playlists")
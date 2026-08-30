import requests
import json
import time
import os
import hmac
import hashlib
from threading import Timer
from dotenv import load_dotenv
from .exceptions import APIError

load_dotenv()

class VoltaClient:
    def __init__(self, base_url: str = "https://api.volta-music.com", token_file: str = "config/token.json"):
        self.token_file = token_file
        self.base_url = base_url
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.token_data = self._load_token()
        self.token = self.token_data.get("access_token")
        self.refresh_interval = int(self.token_data.get("expires_in", 3600))
        self._refresh_counter = self.refresh_interval
        self._refresh_timer = None
        self._save_tick = 0
        self._save_interval = 30  # seconds
        self._start_background_refresh()

    def _refresh_token(self):
        url = f"{self.base_url}/api/v1/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            token_data = response.json()
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f)
            return token_data
        else:
            raise APIError(f"Failed to refresh token: {response.status_code} - {response.text}")

    def _load_token(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
            return token_data
        else:
            return self._refresh_token()

    def _start_background_refresh(self):
        if self._refresh_timer is not None:
            self._refresh_timer.cancel()
        self._refresh_timer = Timer(1, self._background_refresh_tick)
        self._refresh_timer.daemon = True
        self._refresh_timer.start()

    def _background_refresh_tick(self):
        self._refresh_counter -= 1
        self._save_tick += 1
        if self._save_tick >= self._save_interval:
            try:
                self._save_remaning_time()
            except Exception:
                # fail silently to avoid stopping the timer
                pass
            self._save_tick = 0
        if self._refresh_counter <= 0:
            self.token_data = self._refresh_token()
            self.token = self.token_data.get("access_token")
            self.refresh_interval = int(self.token_data.get("expires_in", 3600))
            self._refresh_counter = self.refresh_interval
        self._refresh_timer = Timer(1, self._background_refresh_tick)
        self._refresh_timer.daemon = True
        self._refresh_timer.start()

    def _print_remaning_time(self):
        minutes, seconds = divmod(self._refresh_counter, 60)
        print(f"Time until next token refresh: {minutes}m {seconds}s")

    def _save_remaning_time(self):
        with open(self.token_file, 'r') as f:
            token_data = json.load(f)
        token_data['expires_in'] = self._refresh_counter
        with open(self.token_file, 'w') as f:
            json.dump(token_data, f)

    def stop_background_refresh(self):
        if self._refresh_timer is not None:
            self._refresh_timer.cancel()
            self._refresh_timer = None

    class GET:
        def __init__(self):
            self.client = VoltaClient()

        def GETrequests(self, endpoint: str, params: str = None):
            """
            make a GET request to the Volta API with the provided endpoint and optional parameters.
            """
            if params:
                url = f"{self.client.base_url}{endpoint}/{params}"
            else:
                url = f"{self.client.base_url}{endpoint}"
            headers = {"Authorization": f"Bearer {self.client.token}"}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                raise APIError(f"GET request failed: {response.status_code} - {response.text}")
        class Library:
            def __init__(self):
                self.client = VoltaClient()
                self.endpoint = "/api/v1/library"
                self.GETrequests = self.client.GET().GETrequests
            def tracks(self):
                """
                Get the list of tracks from the Volta API.
                """
                endpoint = f"{self.endpoint}/tracks"
                return self.GETrequests(endpoint)
            def albums(self):
                """
                Get the list of albums from the Volta API.
                """
                endpoint = f"{self.endpoint}/albums"
                return self.GETrequests(endpoint)
            def artists(self):
                """
                Get the list of artists from the Volta API.
                """
                endpoint = f"{self.endpoint}/artists"
                return self.GETrequests(endpoint)
            def artist_albums(self, id: str):
                """
                Get the list of albums for a specific artist from the Volta API.
                """
                endpoint = f"{self.endpoint}/artists/{id}/albums"
                return self.GETrequests(endpoint)
            def artist_tracks(self, id: str):
                """
                Get the list of tracks for a specific artist from the Volta API.
                """
                endpoint = f"{self.endpoint}/artists/{id}/tracks"
                return self.GETrequests(endpoint)
            def playlists(self, id: str = None):
                """
                Get the list of playlists from the Volta API.
                """
                endpoint = f"{self.endpoint}/playlists"
                return self.GETrequests(endpoint, id)
    
    def test(self):
        print("Test function in VoltaClient called.")
        print(f"Base URL: {self.base_url}")
        print(f"Token file: {self.token_file}")
        print(f"Client ID: {self.client_id}")
        print(f"Client Secret: {self.client_secret}")
        print(f"Token: {self.token}")

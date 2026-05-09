"""WHOOP OAuth2 PKCE authentication flow with token persistence."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread

import httpx

AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
SCOPES = "read:recovery read:sleep read:workout read:cycles read:body_measurement offline"
REDIRECT_URI = "http://localhost:8484/callback"
TOKEN_FILE = Path.home() / ".cache" / "whoop_ai_trainer" / "tokens.json"


def _pkce_pair() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def _save_tokens(tokens: dict) -> None:
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(tokens, indent=2))
    TOKEN_FILE.chmod(0o600)


def _load_tokens() -> dict | None:
    if TOKEN_FILE.exists():
        return json.loads(TOKEN_FILE.read_text())
    return None


def _refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> dict:
    resp = httpx.post(TOKEN_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    })
    resp.raise_for_status()
    tokens = resp.json()
    _save_tokens(tokens)
    return tokens


def get_access_token(client_id: str, client_secret: str) -> str:
    """Return a valid access token, refreshing or launching OAuth flow as needed."""
    tokens = _load_tokens()

    if tokens and tokens.get("refresh_token"):
        try:
            tokens = _refresh_access_token(client_id, client_secret, tokens["refresh_token"])
            return tokens["access_token"]
        except httpx.HTTPStatusError:
            pass  # fall through to full auth flow

    # Full PKCE flow
    verifier, challenge = _pkce_pair()
    state = secrets.token_urlsafe(16)

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    code_holder: dict = {}

    class _Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # silence server logs
            pass

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            if "code" in qs:
                code_holder["code"] = qs["code"][0]
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"<h2>WHOOP connected. You can close this tab.</h2>")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"<h2>Auth failed. No code received.</h2>")

    server = HTTPServer(("localhost", 8484), _Handler)
    thread = Thread(target=server.handle_request, daemon=True)
    thread.start()

    print(f"\nOpening browser for WHOOP login...\n{auth_url}\n")
    webbrowser.open(auth_url)
    thread.join(timeout=120)
    server.server_close()

    if "code" not in code_holder:
        raise RuntimeError("OAuth timed out — no authorization code received.")

    resp = httpx.post(TOKEN_URL, data={
        "grant_type": "authorization_code",
        "code": code_holder["code"],
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": verifier,
    })
    resp.raise_for_status()
    tokens = resp.json()
    _save_tokens(tokens)
    return tokens["access_token"]

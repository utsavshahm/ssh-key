import time
import subprocess
import requests
from sshkey.lib.ui import info, success, warn, error, console, divider, blank

# Register a free OAuth app at github.com/settings/developers
# Enable Device Flow, set homepage to your repo URL
# Paste your Client ID below
CLIENT_ID = "Ov23liKC0NLSR9l2oBZP"

DEVICE_CODE_URL = "https://github.com/login/device/code"
TOKEN_URL = "https://github.com/login/oauth/access_token"
API_BASE = "https://api.github.com"


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def start_device_flow() -> str:
    """Run OAuth device flow, return access token."""
    res = requests.post(
        DEVICE_CODE_URL,
        json={
            "client_id": CLIENT_ID,
            "scope": "write:public_key read:user user:email",
        },
        headers={"Accept": "application/json"},
    )
    res.raise_for_status()
    data = res.json()

    device_code = data["device_code"]
    user_code = data["user_code"]
    verification_uri = data["verification_uri"]
    interval = data.get("interval", 5)
    expires_in = data.get("expires_in", 900)

    blank()
    divider()
    console.print(f"[bold]  Open this URL in your browser:[/]")
    console.print(f"  [accent]{verification_uri}[/]")
    blank()
    console.print(f"[bold]  Enter this code:[/]  [accent bold]{user_code}[/]")
    divider()
    blank()

    # auto-open browser
    try:
        subprocess.Popen(["explorer.exe", verification_uri])
    except Exception:
        pass  # silently skip if explorer.exe not available

    info("waiting for you to authorize in the browser...")
    blank()

    deadline = time.time() + expires_in
    while time.time() < deadline:
        time.sleep(interval)
        poll = requests.post(
            TOKEN_URL,
            json={
                "client_id": CLIENT_ID,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
            headers={"Accept": "application/json"},
        )
        poll.raise_for_status()
        result = poll.json()

        if "access_token" in result:
            success("authorized!")
            return result["access_token"]

        err = result.get("error", "")
        if err == "authorization_pending":
            continue
        elif err == "slow_down":
            interval += 5
        elif err == "expired_token":
            error("code expired — please run the command again")
        elif err == "access_denied":
            error("authorization denied")

    error("timed out waiting for authorization")
    return ""


def get_user(token: str) -> dict:
    """Return GitHub user info: login, email."""
    res = requests.get(f"{API_BASE}/user", headers=_headers(token))
    res.raise_for_status()
    user = res.json()

    # email can be null if user hides it — fetch from emails endpoint
    email = user.get("email")
    if not email:
        emails_res = requests.get(f"{API_BASE}/user/emails", headers=_headers(token))
        emails_res.raise_for_status()
        primary = next((e for e in emails_res.json() if e["primary"]), None)
        email = primary["email"] if primary else ""

    return {"username": user["login"], "email": email}


def upload_ssh_key(token: str, title: str, public_key: str) -> str:
    """Upload SSH public key to GitHub, return the key ID."""
    res = requests.post(
        f"{API_BASE}/user/keys",
        json={
            "title": title,
            "key": public_key.strip(),
        },
        headers=_headers(token),
    )

    if res.status_code == 422:
        warn("this key is already on GitHub — fetching existing key ID")
        # find and return the existing key ID by matching public key content
        keys_res = requests.get(f"{API_BASE}/user/keys", headers=_headers(token))
        keys_res.raise_for_status()
        for key in keys_res.json():
            if key["key"].strip() in public_key.strip():
                return str(key["id"])
        return ""

    res.raise_for_status()
    success("SSH key uploaded to GitHub")
    return str(res.json()["id"])


def delete_ssh_key(token: str, key_id: str):
    """Delete SSH key from GitHub account by key ID."""
    res = requests.delete(f"{API_BASE}/user/keys/{key_id}", headers=_headers(token))
    if res.status_code == 204:
        success("SSH key deleted from GitHub")
    elif res.status_code == 404:
        warn("key not found on GitHub — may have already been deleted")
    else:
        res.raise_for_status()


def verify_connection(alias: str) -> str | None:
    """Test SSH connection, return GitHub username or None."""
    info("verifying SSH connection to GitHub...")
    result = subprocess.run(
        ["ssh", "-T", f"git@github-{alias}", "-o", "StrictHostKeyChecking=no"],
        capture_output=True,
        text=True,
    )
    output = result.stderr + result.stdout
    if "successfully authenticated" in output:
        import re

        match = re.search(r"Hi ([^!]+)!", output)
        username = match.group(1) if match else "unknown"
        success(f"connected as [bold]@{username}[/]")
        return username
    return None

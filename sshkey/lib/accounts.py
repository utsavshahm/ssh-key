from pathlib import Path
import csv

SSHKEY_DIR = Path.home() / ".sshkey"
ACCOUNTS_FILE = SSHKEY_DIR / "accounts"

# file format: alias|github_username|email|key_path

def ensure():
    SSHKEY_DIR.mkdir(exist_ok=True)
    if not ACCOUNTS_FILE.exists():
        ACCOUNTS_FILE.touch()

def load() -> list[dict]:
    ensure()
    accounts = []
    for line in ACCOUNTS_FILE.read_text().splitlines():
        parts = line.strip().split("|")
        if len(parts) == 4:
            accounts.append({
                "alias":    parts[0],
                "username": parts[1],
                "email":    parts[2],
                "key_path": parts[3],
            })
    return accounts

def save(alias: str, username: str, email: str, key_path: str):
    ensure()
    accounts = [a for a in load() if a["alias"] != alias]
    accounts.append({"alias": alias, "username": username, "email": email, "key_path": key_path})
    ACCOUNTS_FILE.write_text(
        "\n".join(f"{a['alias']}|{a['username']}|{a['email']}|{a['key_path']}" for a in accounts)
        + "\n"
    )

def get(alias: str) -> dict | None:
    return next((a for a in load() if a["alias"] == alias), None)

def count() -> int:
    return len(load())

def pick_menu() -> dict:
    from sshkey.lib.ui import header, error, console, blank
    accounts = load()
    if not accounts:
        error("no accounts saved yet — run [accent]sshkey add-account[/] first")

    console.print("  pick an account:\n")
    for i, a in enumerate(accounts, 1):
        console.print(f"  [bold][{i}][/] {a['alias']}  [accent](@{a['username']})[/]")

    blank()
    choice = console.input("  enter number: ").strip()

    try:
        idx = int(choice) - 1
        assert 0 <= idx < len(accounts)
    except (ValueError, AssertionError):
        error("invalid choice")
        return {}

    return accounts[idx]

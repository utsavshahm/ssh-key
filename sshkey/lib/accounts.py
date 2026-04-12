from pathlib import Path

SSHKEY_DIR = Path.home() / ".sshkey"
ACCOUNTS_FILE = SSHKEY_DIR / "accounts"

# format: alias|username|email|key_path|github_key_id


def ensure():
    SSHKEY_DIR.mkdir(exist_ok=True)
    if not ACCOUNTS_FILE.exists():
        ACCOUNTS_FILE.touch()
        ACCOUNTS_FILE.chmod(0o600)


def load() -> list[dict]:
    ensure()
    accounts = []
    for line in ACCOUNTS_FILE.read_text().splitlines():
        parts = line.strip().split("|")
        if len(parts) >= 4:
            accounts.append(
                {
                    "alias": parts[0],
                    "username": parts[1],
                    "email": parts[2],
                    "key_path": parts[3],
                    "github_key_id": parts[4] if len(parts) > 4 else "",
                }
            )
    return accounts


def save(alias: str, username: str, email: str, key_path: str, github_key_id: str = ""):
    ensure()
    accounts = [a for a in load() if a["alias"] != alias]
    accounts.append(
        {
            "alias": alias,
            "username": username,
            "email": email,
            "key_path": key_path,
            "github_key_id": github_key_id,
        }
    )
    lines = [
        f"{a['alias']}|{a['username']}|{a['email']}|{a['key_path']}|{a['github_key_id']}"
        for a in accounts
    ]
    ACCOUNTS_FILE.write_text("\n".join(lines) + "\n")
    ACCOUNTS_FILE.chmod(0o600)


def remove(alias: str):
    accounts = [a for a in load() if a["alias"] != alias]
    lines = [
        f"{a['alias']}|{a['username']}|{a['email']}|{a['key_path']}|{a['github_key_id']}"
        for a in accounts
    ]
    ACCOUNTS_FILE.write_text("\n".join(lines) + "\n")


def get(alias: str) -> dict | None:
    return next((a for a in load() if a["alias"] == alias), None)


def count() -> int:
    return len(load())


def pick_menu() -> dict:
    from sshkey.lib.ui import error, console, blank

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

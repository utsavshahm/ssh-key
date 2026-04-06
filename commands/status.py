import subprocess
from sshkey.lib import ui, accounts, github


def run_status():
    ui.header("sshkey status")

    try:
        remote = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
    except subprocess.CalledProcessError:
        ui.warn("no remote set for this repo")
        return

    ui.console.print(f"  remote:  [accent]{remote}[/]")

    # extract alias from remote
    import re
    match = re.search(r"git@github-([^:]+):", remote)
    if not match:
        ui.warn("this repo is not managed by sshkey")
        ui.console.print("  run [bold]sshkey init[/] to link an account")
        return

    alias   = match.group(1)
    account = accounts.get(alias)

    if account:
        ui.console.print(f"  account: [bold]{alias}[/]")
        ui.console.print(f"  github:  [accent]@{account['username']}[/]")
        ui.console.print(f"  email:   {account['email']}")
        ui.console.print(f"  key:     {account['key_path']}")
    else:
        ui.console.print(f"  account: [bold]{alias}[/] [dim](not in accounts file)[/]")

    ui.blank()
    result = github.verify_connection(alias)
    if not result:
        ui.warn(f"connection failed — run: ssh -T git@github-{alias}")


def run_accounts():
    ui.header("saved accounts")
    all_accounts = accounts.load()
    if not all_accounts:
        ui.warn("no accounts yet — run [accent]sshkey add-account[/]")
        return
    for a in all_accounts:
        ui.console.print(f"  [bold]{a['alias']}[/]  [accent]@{a['username']}[/]  {a['email']}  →  {a['key_path']}")
    ui.blank()

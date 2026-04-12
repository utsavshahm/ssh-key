from pathlib import Path
from sshkey.lib import ui, accounts, github, ssh


def run():
    ui.header("remove a GitHub account")

    account = accounts.pick_menu()
    alias = account["alias"]
    key_path = account["key_path"]
    github_key_id = account["github_key_id"]

    ui.blank()
    ui.console.print(f"  [bold]this will:[/]")
    ui.console.print(f"  • delete SSH key from GitHub")
    ui.console.print(f"  • delete key files: {key_path} + .pub")
    ui.console.print(f"  • remove SSH config block for '{alias}'")
    ui.console.print(f"  • remove from sshkey accounts")
    ui.blank()

    confirm = ui.console.input("  are you sure? (y/n): ").strip().lower()
    if confirm != "y":
        ui.warn("cancelled")
        return

    ui.blank()

    # oauth to authorize deletion
    ui.info("authorize on GitHub to confirm deletion...")
    token = github.start_device_flow()

    # delete from github
    if github_key_id:
        github.delete_ssh_key(token, github_key_id)
    else:
        ui.warn("no GitHub key ID stored — skipping GitHub deletion")

    # remove host block from ~/.ssh/config
    ssh.remove_host_block(alias)
    ui.success(f"SSH config block removed for '{alias}'")

    # delete key files
    key = Path(key_path)
    pub = Path(f"{key_path}.pub")
    if key.exists():
        key.unlink()
        ui.success(f"deleted {key_path}")
    if pub.exists():
        pub.unlink()
        ui.success(f"deleted {key_path}.pub")

    # remove from accounts file
    accounts.remove(alias)
    ui.success(f"account '{alias}' removed")

    ui.blank()
    ui.console.print("  run [accent]sshkey accounts[/] to see remaining accounts")

from sshkey.lib import ui, accounts, github, ssh


def run():
    ui.header("load accounts from ~/.ssh/config")

    blocks = ssh.read_existing_blocks()

    if not blocks:
        ui.warn("no [bold]Host github-*[/] blocks found in ~/.ssh/config")
        return

    ui.console.print(f"  found [bold]{len(blocks)}[/] block(s):\n")
    for b in blocks:
        ui.console.print(f"  [accent]{b['alias']}[/]  →  {b['key_path']}")

    ui.blank()
    confirm = ui.console.input("  import all? (y/n): ").strip().lower()
    if confirm != "y":
        ui.warn("cancelled")
        return

    ui.blank()

    for block in blocks:
        alias    = block["alias"]
        key_path = block["key_path"]

        if accounts.get(alias):
            ui.warn(f"'{alias}' already saved — skipping")
            continue

        ui.info(f"importing '[bold]{alias}[/]'...")

        # oauth to get user info
        ui.info("starting GitHub authorization to fetch your identity...")
        token    = github.start_device_flow()
        user     = github.get_user(token)
        username = user["username"]
        email    = user["email"]

        # verify ssh connection
        github.verify_connection(alias)

        accounts.save(alias, username, email, key_path)
        ui.success(f"'{alias}' saved as [accent]@{username}[/]")
        ui.blank()

    ui.success("done — run [accent]sshkey accounts[/] to see all saved accounts")

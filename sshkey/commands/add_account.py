from pathlib import Path
from sshkey.lib import ui, accounts, github, ssh


def run():
    ui.header("add a GitHub account")

    # get label
    alias = ui.console.input("  account label (e.g. work, personal): ").strip().replace(" ", "-")
    if not alias:
        ui.error("label cannot be empty")

    # key path
    default_path = str(Path.home() / ".ssh" / f"id_ed25519_{alias}")
    key_input = ui.console.input(f"  key path [[{default_path}]]: ").strip()
    key_path = key_input or default_path
    key_path = str(Path(key_path).expanduser())

    ui.blank()

    # oauth flow — get token + user info
    ui.info("starting GitHub authorization...")
    token = github.start_device_flow()
    user  = github.get_user(token)
    username = user["username"]
    email    = user["email"]

    ui.blank()

    # generate key if needed
    if Path(key_path).exists():
        ui.warn(f"key already exists at {key_path} — skipping generation")
    else:
        ssh.generate_key(email, key_path)

    # write ssh config
    if ssh.host_block_exists(alias):
        ui.warn(f"SSH config block for '{alias}' already exists — updating")
        ssh.remove_host_block(alias)
    ssh.write_host_block(alias, key_path)

    # upload key to github
    public_key = Path(f"{key_path}.pub").read_text().strip()
    github.upload_ssh_key(token, f"sshkey-{alias}", public_key)

    # add to agent
    ssh.add_key_to_agent(key_path)

    # verify
    github.verify_connection(alias)

    # save account
    accounts.save(alias, username, email, key_path)

    ui.blank()
    ui.success(f"account '[bold]{alias}[/]' saved — run [accent]sshkey init[/] in any project to use it")

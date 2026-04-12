from pathlib import Path
from sshkey.lib import ui, accounts, github, ssh


def run():
    ui.header("add a GitHub account")

    # get label
    alias = (
        ui.console.input("  account label (e.g. work, personal): ")
        .strip()
        .replace(" ", "-")
    )
    if not alias:
        ui.error("label cannot be empty")

    # key name only — always stored in ~/.ssh/
    default_name = f"id_ed25519_{alias}"
    key_name = ui.console.input(f"  key name [[{default_name}]]: ").strip()
    key_name = key_name or default_name
    key_path = str(Path.home() / ".ssh" / key_name)

    ui.blank()

    # oauth flow — get token + user info
    ui.info("starting GitHub authorization...")
    token = github.start_device_flow()
    user = github.get_user(token)
    username = user["username"]
    email = user["email"]

    ui.blank()

    # generate key (handles overwrite prompt internally)
    ssh.generate_key(email, key_path)

    # write ssh config
    if ssh.host_block_exists(alias):
        ui.warn(f"SSH config block for '{alias}' already exists — updating")
        ssh.remove_host_block(alias)
    ssh.write_host_block(alias, key_path)

    # upload key to github, get key ID
    public_key = Path(f"{key_path}.pub").read_text().strip()
    github_key_id = github.upload_ssh_key(token, f"sshkey-{alias}", public_key)

    # add to agent
    ssh.add_key_to_agent(key_path)

    # verify
    github.verify_connection(alias)

    # save account with key ID
    accounts.save(alias, username, email, key_path, github_key_id)

    ui.blank()
    ui.success(
        f"account '[bold]{alias}[/]' saved — run [accent]sshkey init[/] in any project to use it"
    )

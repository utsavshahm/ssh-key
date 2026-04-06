from sshkey.lib import ui, accounts, ssh


def run():
    ui.header("link a GitHub account to this project")

    if not ssh.is_git_repo():
        ui.error("not inside a git repo — run [bold]git init[/] first")

    account = accounts.pick_menu()

    ui.blank()
    ui.info(f"setting up '[bold]{account['alias']}[/]' for this project...")

    ssh.add_key_to_agent(account["key_path"])
    ssh.rewrite_remote(account["alias"])
    ssh.set_git_identity(account["email"], account["username"])

    ui.blank()
    ui.success(f"done! this project will always use '[bold]{account['alias']}[/]'")
    ui.console.print("  [bold]git push, git pull[/] — just work from here on.")

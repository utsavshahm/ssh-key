import sys
from sshkey.lib.ui import console


HELP = """
[bold cyan]sshkey[/] — multiple GitHub accounts, zero headache

  [bold]sshkey add-account[/]    add a GitHub account (OAuth + auto key upload)
  [bold]sshkey load-account[/]   import accounts from existing ~/.ssh/config
  [bold]sshkey init[/]           link an account to this project
  [bold]sshkey status[/]         show which account this project uses
  [bold]sshkey accounts[/]       list all saved accounts

  [cyan]workflow:[/]
    1. sshkey add-account    ← once per github account
    2. cd your-project
    3. sshkey init           ← once per project
    4. git push / git pull   ← works forever
"""


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "add-account":
        from sshkey.commands.add_account import run
        run()
    elif cmd == "load-account":
        from sshkey.commands.load_account import run
        run()
    elif cmd == "init":
        from sshkey.commands.init import run
        run()
    elif cmd == "status":
        from sshkey.commands.status import run_status
        run_status()
    elif cmd == "accounts":
        from sshkey.commands.status import run_accounts
        run_accounts()
    elif cmd in ("help", "--help", "-h"):
        console.print(HELP)
    else:
        console.print(f"[red]unknown command: {cmd}[/]")
        console.print(HELP)
        sys.exit(1)


if __name__ == "__main__":
    main()

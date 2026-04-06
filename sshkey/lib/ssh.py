import subprocess
from pathlib import Path
from sshkey.lib.ui import info, success, warn, error, console

SSH_CONFIG = Path.home() / ".ssh" / "config"


def ensure_ssh_dir():
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(exist_ok=True)
    if not SSH_CONFIG.exists():
        SSH_CONFIG.touch()
        SSH_CONFIG.chmod(0o600)


def host_block_exists(alias: str) -> bool:
    return f"Host github-{alias}" in SSH_CONFIG.read_text()


def write_host_block(alias: str, key_path: str):
    ensure_ssh_dir()
    with SSH_CONFIG.open("a") as f:
        f.write(f"\n# sshkey: {alias}\n")
        f.write(f"Host github-{alias}\n")
        f.write(f"  HostName github.com\n")
        f.write(f"  User git\n")
        f.write(f"  IdentityFile {key_path}\n")
        f.write(f"  IdentitiesOnly yes\n")
        f.write(f"  AddKeysToAgent yes\n")
    success(f"SSH config block written for '{alias}'")


def remove_host_block(alias: str):
    lines = SSH_CONFIG.read_text().splitlines()
    new_lines = []
    skip = False
    for line in lines:
        if line.strip() == f"# sshkey: {alias}":
            skip = True
        if skip and line.strip() == "" and new_lines and new_lines[-1].strip() == "":
            skip = False
            continue
        if not skip:
            new_lines.append(line)
    SSH_CONFIG.write_text("\n".join(new_lines))


def read_existing_blocks() -> list[dict]:
    """Parse existing Host github-* blocks from ~/.ssh/config."""
    ensure_ssh_dir()
    blocks = []
    current = {}
    for line in SSH_CONFIG.read_text().splitlines():
        line = line.strip()
        if line.startswith("Host github-"):
            if current:
                blocks.append(current)
            current = {"alias": line.replace("Host github-", "").strip()}
        elif current:
            if line.startswith("IdentityFile"):
                current["key_path"] = line.split(None, 1)[1].strip()
    if current:
        blocks.append(current)
    return [b for b in blocks if "key_path" in b]


def generate_key(email: str, key_path: str):
    result = subprocess.run(
        ["ssh-keygen", "-t", "ed25519", "-C", email, "-f", key_path, "-N", ""],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        error(f"key generation failed: {result.stderr}")
    success(f"SSH key generated at {key_path}")


def add_key_to_agent(key_path: str):
    result = subprocess.run(["ssh-add", key_path], capture_output=True, text=True)
    if result.returncode == 0:
        success("key added to agent")
    else:
        warn("could not add key to agent — you may need to run ssh-agent manually")


def rewrite_remote(alias: str):
    try:
        current = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        repo = current
        for prefix in ["https://github.com/", "git@github.com:"]:
            repo = repo.replace(prefix, "")
        repo = repo.removesuffix(".git")
        new_remote = f"git@github-{alias}:{repo}.git"
        subprocess.run(["git", "remote", "set-url", "origin", new_remote], check=True)
        success(f"remote updated to {new_remote}")
    except subprocess.CalledProcessError:
        repo = console.input("  no remote found — enter your GitHub [bold]user/repo[/]: ").strip()
        repo = repo.removesuffix(".git")
        new_remote = f"git@github-{alias}:{repo}.git"
        subprocess.run(["git", "remote", "add", "origin", new_remote], check=True)
        success(f"remote set to {new_remote}")


def set_git_identity(email: str, username: str):
    subprocess.run(["git", "config", "--local", "user.email", email], check=True)
    subprocess.run(["git", "config", "--local", "user.name", username], check=True)
    success(f"git identity set to [bold]{username}[/] <{email}>")


def is_git_repo() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        capture_output=True
    )
    return result.returncode == 0

# sshkey

Manage multiple GitHub accounts from Git Bash on Windows — without touching SSH config files, remembering `ssh-add` commands, or breaking your head every time you switch projects.

```bash
sshkey add-account   # set up a github account once
sshkey init          # link it to a project once
git push             # just works, forever
```

---

## the problem

If you have two GitHub accounts — work and personal — every project becomes a puzzle:

- Which key is loaded?
- Why is it pushing from the wrong account?
- What was that `ssh-add` command again?
- Why did it stop working after a restart?

`sshkey` solves this once, per project, and then gets out of your way.

---

## install

**Requirements:** Git Bash on Windows (comes with Git for Windows)

**1. Download the script**

```bash
mkdir -p ~/scripts
curl -o ~/scripts/sshkey.sh https://raw.githubusercontent.com/yourusername/sshkey/main/sshkey.sh
chmod +x ~/scripts/sshkey.sh
```

**2. Add to your PATH**

```bash
echo 'export PATH="$HOME/scripts:$PATH"' >> ~/.bashrc
echo 'alias sshkey="bash ~/scripts/sshkey.sh"' >> ~/.bashrc
source ~/.bashrc
```

**3. Done**

```bash
sshkey help
```

---

## usage

### add a GitHub account (once per account)

```bash
sshkey add-account
```

This will:
- Ask for a label (e.g. `work`, `personal`)
- Generate an SSH key at `~/.ssh/id_ed25519_work`
- Print the public key for you to paste into GitHub
- Wait while you add it at [github.com/settings/ssh/new](https://github.com/settings/ssh/new)
- Verify the connection automatically

### link an account to a project (once per project)

```bash
cd /c/projects/my-work-project
sshkey init
```

Shows a menu of your saved accounts, you pick one, it handles the rest:
- Rewrites the git remote to use the right SSH key
- Adds the key to the agent

From here, `git push` and `git pull` just work — no extra steps, ever.

### check status

```bash
sshkey status
```

Shows which account this project is using and verifies the connection is live.

### list all accounts

```bash
sshkey accounts
```

---

## how it works

Under the hood, `sshkey` uses SSH config `Host` aliases — the correct, stable way to handle multiple GitHub accounts:

```
# ~/.ssh/config (managed by sshkey, don't edit manually)

Host github-work
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_work
  IdentitiesOnly yes
```

Your project's git remote points to `git@github-work:you/repo.git` instead of `git@github.com:you/repo.git`. Git doesn't know the difference. SSH routes it to the right key automatically.

---

## faq

**Does it work in PowerShell?**
No — use Git Bash. Supporting both is where the real complexity begins and the value drops fast.

**What if I already have SSH keys?**
`sshkey add-account` will detect an existing key at the path and skip generation. You just need to make sure it's already on GitHub.

**Will it break my existing git setup?**
It only changes the `origin` remote URL of projects you explicitly run `sshkey init` in. Everything else is untouched.

**Does it survive restarts?**
The SSH config is permanent. On restart, the agent needs to reload keys — but because `sshkey` uses `AddKeysToAgent yes` in the config, the first `git push` after restart will prompt once and cache it.

---

## license

MIT
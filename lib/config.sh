#!/usr/bin/env bash

SSH_CONFIG="$HOME/.ssh/config"

_ensure_ssh_config() {
  mkdir -p "$HOME/.ssh"
  touch "$SSH_CONFIG"
  chmod 600 "$SSH_CONFIG"
}

_host_block_exists() {
  local alias="$1"
  grep -q "^Host github-${alias}$" "$SSH_CONFIG" 2>/dev/null
}

_write_host_block() {
  local alias="$1" key_path="$2"
  cat >> "$SSH_CONFIG" <<EOF

# sshkey: ${alias}
Host github-${alias}
  HostName github.com
  User git
  IdentityFile ${key_path}
  IdentitiesOnly yes
  AddKeysToAgent yes
EOF
  success "SSH config block written for '${alias}'"
}

_remove_host_block() {
  local alias="$1"
  sed -i "/^# sshkey: ${alias}$/,/^$/d" "$SSH_CONFIG" 2>/dev/null || true
}

_rewrite_remote() {
  local alias="$1"
  local current_remote
  current_remote=$(git remote get-url origin 2>/dev/null || true)

  if [ -z "$current_remote" ]; then
    read -rp "  no remote found. enter your GitHub user/repo (e.g. john/myproject): " repo_input
    repo_input="${repo_input#https://github.com/}"
    repo_input="${repo_input#git@github.com:}"
    repo_input="${repo_input%.git}"
    git remote add origin "git@github-${alias}:${repo_input}.git"
    success "remote added: git@github-${alias}:${repo_input}.git"
  else
    local repo_path
    repo_path=$(echo "$current_remote" | sed -E 's|https://github.com/||; s|git@github[^:]*:||; s|\.git$||')
    git remote set-url origin "git@github-${alias}:${repo_path}.git"
    success "remote updated: git@github-${alias}:${repo_path}.git"
  fi
}
#!/usr/bin/env bash

SSHKEY_DIR="$HOME/.sshkey"

_ensure_agent() {
  if [ -z "${SSH_AUTH_SOCK:-}" ] || ! ssh-add -l &>/dev/null; then
    eval "$(ssh-agent -s)" > /dev/null
    echo "export SSH_AUTH_SOCK=$SSH_AUTH_SOCK" > "$SSHKEY_DIR/agent.env"
    echo "export SSH_AGENT_PID=$SSH_AGENT_PID" >> "$SSHKEY_DIR/agent.env"
  fi
}

_add_key_to_agent() {
  local key_path="$1"
  _ensure_agent
  if ! ssh-add -l 2>/dev/null | grep -q "$key_path"; then
    ssh-add "$key_path" 2>/dev/null \
      && success "key added to agent" \
      || warn "could not add key to agent (passphrase protected?)"
  fi
}

_verify_github() {
  local alias="$1"
  info "verifying connection to GitHub..."
  local result
  result=$(ssh -T "git@github-${alias}" 2>&1 || true)
  if echo "$result" | grep -q "successfully authenticated"; then
    local username
    username=$(echo "$result" | grep -oP "Hi \K[^!]+")
    success "connected as ${BOLD}${username}${RESET}"
    echo "$username"
    return 0
  else
    return 1
  fi
}
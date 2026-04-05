#!/usr/bin/env bash

cmd_add_account() {
  header "add a GitHub account"

  read -rp "  account label (e.g. work, personal): " alias
  alias="${alias// /-}"
  [ -z "$alias" ] && error "label cannot be empty"

  local default_path="$HOME/.ssh/id_ed25519_${alias}"
  read -rp "  key path [${default_path}]: " key_path
  key_path="${key_path:-$default_path}"
  key_path="${key_path/#\~/$HOME}"

  echo ""

  if [ -f "$key_path" ]; then
    warn "key already exists at ${key_path}, skipping generation"
  else
    read -rp "  your GitHub email: " email
    [ -z "$email" ] && error "email cannot be empty"
    ssh-keygen -t ed25519 -C "$email" -f "$key_path" -N "" > /dev/null
    success "key generated at ${key_path}"
  fi

  echo ""

  if _host_block_exists "$alias"; then
    warn "SSH config block for '${alias}' already exists, updating..."
    _remove_host_block "$alias"
  fi
  _write_host_block "$alias" "$key_path"

  _add_key_to_agent "$key_path"

  echo ""
  divider
  echo -e "${BOLD}  Add this public key to GitHub:${RESET}"
  divider
  echo ""
  cat "${key_path}.pub"
  echo ""
  divider
  echo ""
  echo -e "  Go to: ${CYAN}https://github.com/settings/ssh/new${RESET}"
  echo -e "  Paste the key above and save it."
  echo ""

  read -rp "  press enter once you've added it to GitHub..."
  echo ""

  local verified_user
  if verified_user=$(_verify_github "$alias"); then
    _save_account "$alias" "$verified_user" "$key_path"
    echo ""
    success "account '${alias}' saved — run ${BOLD}sshkey init${RESET} in any project to use it"
  else
    warn "could not verify. check GitHub and try: ssh -T git@github-${alias}"
    _save_account "$alias" "unknown" "$key_path"
  fi
}
#!/usr/bin/env bash

cmd_init() {
  header "link a GitHub account to this project"

  git rev-parse --git-dir &>/dev/null || error "not inside a git repo. run 'git init' first."

  local selected_alias
  selected_alias=$(_pick_account_menu)

  local selected_key
  selected_key=$(_get_account_key "$selected_alias")

  echo ""
  info "setting up '${selected_alias}' for this project..."

  _add_key_to_agent "$selected_key"
  _rewrite_remote "$selected_alias"

  echo ""
  success "done! this project will always use '${selected_alias}'"
  echo -e "  ${BOLD}git push, git pull${RESET} — just work from here on."
}

cmd_status() {
  header "sshkey status"

  git rev-parse --git-dir &>/dev/null || error "not inside a git repo"

  local remote
  remote=$(git remote get-url origin 2>/dev/null || true)

  if [ -z "$remote" ]; then
    warn "no remote set for this repo"
    return
  fi

  echo -e "  remote:  ${CYAN}${remote}${RESET}"

  local alias
  alias=$(echo "$remote" | grep -oP 'git@github-\K[^:]+' || true)

  if [ -z "$alias" ]; then
    warn "this repo is not managed by sshkey"
    echo -e "  run ${BOLD}sshkey init${RESET} to link an account"
    return
  fi

  echo -e "  account: ${BOLD}${alias}${RESET}"
  echo -e "  github:  ${CYAN}@$(_get_account_username "$alias")${RESET}"
  echo -e "  key:     $(_get_account_key "$alias")"
  echo ""

  _verify_github "$alias" > /dev/null || warn "could not connect — run: ssh -T git@github-${alias}"
}

cmd_accounts() {
  header "saved accounts"
  local count
  count=$(_account_count)
  if [ "$count" -eq 0 ]; then
    warn "no accounts yet — run ${BOLD}sshkey add-account${RESET}"
    return
  fi
  while IFS='|' read -r alias username key_path; do
    echo -e "  ${BOLD}${alias}${RESET}  ${CYAN}@${username}${RESET}  →  ${key_path}"
  done < "$ACCOUNTS_FILE"
  echo ""
}
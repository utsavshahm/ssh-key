#!/usr/bin/env bash

SSHKEY_DIR="$HOME/.sshkey"
ACCOUNTS_FILE="$SSHKEY_DIR/accounts"

# format: alias|github_username|key_path

_ensure_accounts_file() {
  mkdir -p "$SSHKEY_DIR"
  [ -f "$ACCOUNTS_FILE" ] || touch "$ACCOUNTS_FILE"
}

_save_account() {
  local alias="$1" username="$2" key_path="$3"
  grep -v "^${alias}|" "$ACCOUNTS_FILE" > "${ACCOUNTS_FILE}.tmp" 2>/dev/null || true
  mv "${ACCOUNTS_FILE}.tmp" "$ACCOUNTS_FILE"
  echo "${alias}|${username}|${key_path}" >> "$ACCOUNTS_FILE"
}

_account_count() {
  [ -f "$ACCOUNTS_FILE" ] && grep -c '.' "$ACCOUNTS_FILE" 2>/dev/null || echo 0
}

_get_account_key() {
  local alias="$1"
  grep "^${alias}|" "$ACCOUNTS_FILE" 2>/dev/null | cut -d'|' -f3
}

_get_account_username() {
  local alias="$1"
  grep "^${alias}|" "$ACCOUNTS_FILE" 2>/dev/null | cut -d'|' -f2
}

_pick_account_menu() {
  local count
  count=$(_account_count)
  [ "$count" -eq 0 ] && error "no accounts saved yet. run ${BOLD}sshkey add-account${RESET} first."

  echo -e "  pick an account:\n" >&2
  local i=1
  local aliases=()
  while IFS='|' read -r alias username _ <&3; do
    echo -e "  ${BOLD}[$i]${RESET} ${alias}  ${CYAN}(@${username})${RESET}" >&2
    aliases+=("$alias")
    ((i++))
  done 3< "$ACCOUNTS_FILE"

  echo "" >&2
  read -rp "  enter number: " choice <&/dev/tty
  local idx=$((choice - 1))
  [ "$idx" -lt 0 ] || [ "$idx" -ge "${#aliases[@]}" ] && error "invalid choice"

  echo "${aliases[$idx]}"
}
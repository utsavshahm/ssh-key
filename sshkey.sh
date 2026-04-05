#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# load libs
source "$SCRIPT_DIR/lib/ui.sh"
source "$SCRIPT_DIR/lib/accounts.sh"
source "$SCRIPT_DIR/lib/agent.sh"
source "$SCRIPT_DIR/lib/config.sh"

# load commands
source "$SCRIPT_DIR/commands/add-account.sh"
source "$SCRIPT_DIR/commands/init.sh"

# bootstrap
_ensure_accounts_file
_ensure_ssh_config

cmd_help() {
  echo ""
  echo -e "${BOLD}sshkey${RESET} — multiple GitHub accounts, zero headache"
  echo ""
  echo -e "  ${BOLD}sshkey add-account${RESET}   add a GitHub account"
  echo -e "  ${BOLD}sshkey init${RESET}          link an account to this project"
  echo -e "  ${BOLD}sshkey status${RESET}        show which account this project uses"
  echo -e "  ${BOLD}sshkey accounts${RESET}      list all saved accounts"
  echo ""
  echo -e "  ${CYAN}workflow:${RESET}"
  echo -e "    1. sshkey add-account   ← once per github account"
  echo -e "    2. cd your-project"
  echo -e "    3. sshkey init          ← once per project"
  echo -e "    4. git push / git pull  ← works forever"
  echo ""
}

case "${1:-help}" in
  add-account) cmd_add_account ;;
  init)        cmd_init ;;
  status)      cmd_status ;;
  accounts)    cmd_accounts ;;
  help|--help) cmd_help ;;
  *) echo -e "${RED}unknown command: $1${RESET}"; cmd_help; exit 1 ;;
esac
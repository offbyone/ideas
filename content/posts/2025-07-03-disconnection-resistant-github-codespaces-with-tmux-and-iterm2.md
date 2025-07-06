Title: Disconnection-resistant GitHub codespaces with tmux and iTerm2
Slug: disconnection-resistant-github-codespaces-with-tmux-and-iterm2
Date: 2025-07-03T13:45:24.461789
Tags: github, codespaces, frustration, tmux, iterm2
Category: tools
Author: Chris Rose
Email: offline@offby1.net
Status: published
Toot: https://wandering.shop/@offby1/114791312807855334
Summary: GitHub codespaces' ssh client is prone to frequent, frustrating disconnections. If you're actively working remotely, that means that you often lose state in the codespace, which is especially frustrating if what you are doing takes a long time to set up, or should stay running. This post describes how I mitigate that with a script that ensures I always have a session in my codespace.

I find GitHub Codespaces a true mixed blessing. The uniform development environment is super democratizing, but a lot of the polish hinges on the use of VSCode as a development environment, with the terminal-based development approach feeling like an afterthought a lot of the time. Nowhere, to me, is this more apparent than in the ssh connection approach. `gh codespace ssh` is the way you open an ssh connection to the Codespace terminal, and boy _howdy_ is it unstable. I estimate I lose my connection to a codespace at least once per hour, when actively working on it. If my laptop screen locks, it disconnects every time. If I never had terminal state, that would be fine, but that's not the case most of the time; most days, I've got a server running, possibly multiple. Those terminate in whatever state when the connection is dropped.

Of course, we can all guess what the solution is: "use tmux"; it's the solution to a lot of problems of this shape. However, what I really want is to be able to use tmux and _not have to think about it_, and that's what I'm going to show you here. I put this code in `~/.local/bin/,ghcs-iterm2` so that it is on my `PATH`[ref]I <a href="https://rhodesmill.org/brandon/2009/commands-with-comma/">name all my custom commands starting with a comma</a>[/ref].

```shell
#!/usr/bin/env bash

set -eu
set -o pipefail

SESSION_NAME="${1:-default-session}"

function get_recent_workspaces() {
  gh codespace list \
    --repo "github/github" \
    --json name,gitStatus,lastUsedAt,repository \
    --template "{{range .}}{{.repository}} {{.gitStatus.ref}} last used: {{ slice .lastUsedAt 8 }} _ {{.name}};{{end}}" |
    tr ';' '\n'
}

ws_file=$(mktemp)
cleanup() {
  rm -rf "$ws_file"
}
trap cleanup EXIT

get_recent_workspaces >"$ws_file"

if [ $(cat "$ws_file" | tr -d "\n \t" | wc -c) = 0 ]; then
  echo "No workspaces; create one"
  exit 0
fi

GH_CS_WORKSPACE=$(cat "$ws_file" |
  fzf -1 |
  awk '{print $7}')

if [ "" = "${GH_CS_WORKSPACE}" ]; then
  echo "No workspace selected"
elif [ -n "${GH_CS_WORKSPACE}" ]; then
  echo "Opening codespace $GH_CS_WORKSPACE for session $SESSION_NAME"
  gh cs ssh --codespace "$GH_CS_WORKSPACE" -- -t "tmux -CC new-session -A -s $SESSION_NAME"
fi
```

If you don't use iTerm2, this still works, you just drop the `-CC` from the tmux command.

### Usage

```shellsession
$ ,gcsh-iterm2
```

That's it; that's the whole thing; this script will find the "right" codespace, or let you choose one, and connect to it, opening up the iTerm2 tmux interface for you with the remote session. This is _not_ doing anything special or revolutionary, it's just composing a few basic CLI utilities.

### Requirements

- you need to have `tmux` installed on your codespace. I do that in [the codespaces dotfiles repository](https://docs.github.com/en/codespaces/setting-your-user-preferences/personalizing-github-codespaces-for-your-account) installer.
- your local machine needs the `gh` command line, `fzf`, and `jq` all installed

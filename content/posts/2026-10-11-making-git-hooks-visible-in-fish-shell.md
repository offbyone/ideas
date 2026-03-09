---
title: Making git hooks visible in fish shell
slug: making-git-hooks-visible-in-fish-shell
date: 2026-10-11T09:39:38.552343
tags: 
  - git 
  - fish 
  - shell
category: tools
author: Chris Rose
email: offline@offby1.net
status: published
summary: Inspired by Ned Batchelder's post that was inspired by Frank Wiles' tale of near-hacking, here's a fish shell function that will show you the git hooks that are executable in the current repository.
toot: https://wandering.shop/@offby1/117423301975874610
---

I saw [Ned Batchelder's post about a zsh function to show git hooks in the current repository](https://nedbatchelder.com/blog/202610/making_git_hooks_visible), which was in turn inspired by a [post by Frank Wiles, detailing a hack](https://frankwiles.com/posts/i-got-targeted/) that nearly got him, reliant on sketchy git hooks in a shared folder.

I use [fish shell](https://fishshell.com), though, not zsh, so here's my version of the same script. I put this in `~/.config/fish/functions/_show_git_hooks.fish`:

```fish
function _show_git_hooks --on-variable PWD
    set -l git_dir (git rev-parse --git-dir 2>/dev/null)
    if ! test -d "$git_dir/hooks"
        # clear the shown hooks dir, since we have left a repo
        set -e _git_shown_hooks_dir
        return
    end

    set -l hooks_dir_rel "$git_dir/hooks"
    set -l hooks_dir (realpath -- "$hooks_dir_rel")

    # only announce once per repo, since this function is called on every prompt
    if set -q _git_shown_hooks_dir
        if test "$_git_shown_hooks_dir" = "$hooks_dir"
            return
        end
    end

    set -g _git_shown_hooks_dir "$hooks_dir"

    set -l hooks
    for hook in (find "$hooks_dir" -type f | sort)
        if test -x "$hook"; and not string match -q '*.sample' -- "$hook"; and not string match -q '*.disabled' -- "$hook"; and not string match -q '*.txt' -- "$hook"
            set -a hooks "$hook"
        end
    end
    if test (count $hooks) -gt 0
        echo "Git hooks found in $hooks_dir_rel:"
        for hook in $hooks
            echo "  - "(basename $hook)
        end
    end
end
```

Then, much like in Ned's post, it's necessary to invoke the script on shell intialization, so I've added this to `~/.config/fish/conf.d/git-hooks.fish`: 

```fish
if status is-interactive
    _show_git_hooks
end
```

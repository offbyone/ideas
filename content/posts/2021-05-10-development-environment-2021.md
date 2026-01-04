---
title: Development Environment (2021)
slug: development-environment-2021
date: 2021-05-10 07:34:39.057246
category: tools
tags:
- chezmoi
- doom-emacs
- direnv
- starship
- asdf
- python
- development
author: Chris Rose
status: published
email: offline@offby1.net
summary: Some of the things I use in my day to day computering
---
I've had a good couple of years in terms of tool discovery. Rather than try to tweet about them in bits and bobs, I figured I would write up a few bits and pieces that I like.

# Chezmoi

> If you do not personalize your configuration or only ever use a single operating system with a single account and none of your dotfiles contain secrets then you don't need chezmoi. Otherwise, read on...

Above all else, managing my dotfiles has been the thing I've spent the most time messing around with. I have, variously:

- kept them in CVS
- kept them in SVN
- kept them in Git
- installed them using stow
- installed them using hand-built shell scripts
- installed them using a simple code checkout
- managed multiple dotfile repos with `mr` [ref]This tool has been extraodinarily hard to google whenver it's stumped me[/ref]

It has been a damned nightmare.

Which is why [chezmoi](https://www.chezmoi.io/) has been such a breath of fresh air. Chezmoi combines simple templating, a CLI that can perform basic state management and change management operations, and a small TOML configuration model. I use it for everything that goes in `$HOME` that I care to retain, and I can trivially configure my home and work computers from the same shell configuration.

# Doom Emacs

> Doom is a configuration framework for GNU Emacs tailored for Emacs bankruptcy veterans who want less framework in their frameworks, a modicum of stability (and reproducibility) from their package manager, and the performance of a hand rolled config (or better). It can be a foundation for your own config or a resource for Emacs enthusiasts to learn more about our favorite operating system.

I've been an Emacs user since 2005, after spending [ref]misspending[/ref] my university years using Vim. During that time, I've had a host of different configurations for it. I started off with the one my team at ACI/MessagingDirect used, which was a pretty powerful metaprogramming environment that served me well until I finally added too much cruft and it fell over. I've gone through Prelude and Spacemacs as well, but none of them have fit me quite like [Doom](https://github.com/hlissner/doom-emacs) does. Doom is a strange mix of superbly simple and deeply flexible, which fits Emacs to a tee.

Some of the things that it offers that I really like:

- literate configuration

  My configuration is written in [org-mode](https://orgmode.org/), making it not so much "self-documenting" as it is "a readme that happens to have configuration in it". For one small example:

  ``` org
  Monitor my roam directory for changes (dropbox is the reason here) and re-run
  the roam DB cache build when some are observed.

  Caveat: this is not recursive.

  #+begin_src emacs-lisp
  (after! org-roam
    (file-notify-add-watch org-roam-directory '(change)
                           (lambda (_event)
                             (org-roam-db-build-cache))))
  #+end_src
  ```

- modern development tools

  Doom ships with code completion, LSP support, vim and emacs keybindings, project support, modes for many modern tools.

- community

  Doom has an active and helpful Discord. It's actually the best place to talk about Emacs in general that I've found.

# direnv

> direnv is an extension for your shell. It augments existing shells with a new feature that can load and unload environment variables depending on the current directory.

A year ago I discovered [direnv](https://direnv.net/), which apparently makes me *very* late to the party. The first commit was laid down in 2010, and it solves a problem I've tried to address with a half dozen other tools over the years. In the simplest possible terms, it lets me set project level environment variables.

I have two patterns I use a lot: First, I tend to have my AWS profile set in a top level envrc:

``` bash
export AWS_REGION=us-west-2
export AWS_DEFAULT_REGION=$AWS_REGION
export AWS_PROFILE=chicon
```

Second, on a package by package basis, I will set up things like the runtimes and some specific custom tools:

``` bash
source_up  # what this does is pull in whatever .envrc exists in a higher directory
layout python python3
use pip-tools requirements.in --no-emit-index-url --no-emit-trusted-host
```

This pair here gives me an AWS client already configured to the right profile, using a python 3 virtualenv specific to the project, and thanks to [my direnv and pip-tools integration]({filename}2020-06-16-direnv-and-pip-tools-together.md) some sweet automatic dependency management. This works in every shell and once you have it it's hard to work without it.

Oh, and in case that wasn't awesome enough, Doom Emacs has support for it built in.

# starship

> The minimal, blazing-fast, and infinitely customizable prompt for any shell!
>
> - Fast: it's fast -- really really fast! 🚀
> - Customizable: configure every aspect of your prompt.
> - Universal: works on any shell, on any operating system.
> - Intelligent: shows relevant information at a glance.
> - Feature rich: support for all your favorite tools.
> - Easy: quick to install -- start using it in minutes.

My shell prompt is somewhere I spend a lot of time, and finding one that shows the information I need, and does so quickly. I've gone through a lot of them over the years, all of various degrees of "pretty" and "slow". I finally found one that's fast enough for me, though, and it's a rocket.

Starship is implemented in Rust, and it uses a set of modules alongside support for custom modules to display an elegant prompt in minimal time. I use it to show me the currenet state of my git repo, the SSH keys I have in my agent, and in the case of my work prompt, some internal metadata about the project I'm looking at that otherwise I'd have to keep in my head.

![an animation of a terminal prompt, demonstrating several features of the Starship prompt](%7Bstatic%7D/images/2021-05-10/devenv-starship.gif)

On a personal level, Starship also contains the [first serious Rust code I have ever written](https://github.com/starship/starship/pull/2499) and I'm pretty proud of that.

# asdf

> Manage multiple runtime versions with a single CLI tool

I had been using a mix of `rbenv` and `pyenv` to manage my runtimes for projects. I admit, though, I've gotten tired of trying to keep them all straight in my head. It turns out I'm not alone. [asdf](https://asdf-vm.com/) takes on the problem of managing all of the runtime managers in one simple tool. Instead of a `.python-versions` file, and a ruby one, and a node one... `asdf` uses a single `.tool-versions` to designate all of its pluggable runtimes. It doesn't have as wide-ranging tool support -- I only just got a PR to the emacs mspyls LSP server project merged that allows it to work -- but in most cases no special casing is needed. It's added some much needed simplicity to my devenv.
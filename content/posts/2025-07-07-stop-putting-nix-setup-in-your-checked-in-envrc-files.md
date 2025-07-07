Title: Stop putting nix setup in your checked-in .envrc files
Slug: stop-putting-nix-setup-in-your-checked-in-envrc-files
Date: 2025-07-07T11:05:38.566927
Tags: petpeeve, nix, direnv
Category: programming
Author: Chris Rose
Email: offline@offby1.net
Status: published
Toot: https://wandering.shop/@offby1/114753269522469030
Summary: Nix-using developers who use direnv, please stop checking in your .envrc files; they break your project for other contributors.

This is, as [glyph pointed out a while back](https://mastodon.social/@glyph/114753285581802594), an "extremely specific complaint", but here's the short version:

If you use nix and direnv, it is natural to have a `.envrc` that contains `use flake`; it sets up your local development environment in a friendly way for your tools. You might be tempted to include that `.envrc` file in your repository, so that you don't have to enter that single line of text in any new clone.

_I am asking you, please, do not do that second thing._

I use Direnv extensively and have for years, but I don't use Nix, and am not likely ever to (in part because I'm a macOS user, and Nix is still not friction-free there, but also because I just _don't want to_). I also clone a lot of open source repositories with an eye to making small contributions to them. When one of them contains a checked-in `.envrc` file, though, I'm braced for friction.

What that means is that the first interaction I have with your code is a speedbump in every single tool I use. My editor reads `.envrc` files, so I see errors there. My shell does, too, so that fails. Unless you [perform the workaround I describe in another post]({filename}./2025-06-26-suppressing-use-flake-in-nix-fan-envrc-files.md), _every_ direnv invocation will either fail, or I'll have to maintain a permanently dirty working copy of your repository (which is, in fact, a lot harder if one is trying out [jujutsu](https://jj-vcs.github.io/jj/latest/)).

If it helps to convince you, Direnv itself is described as "Built with Nix" and has a flake configuration, [but _they don't check in their `.envrc`_](https://github.com/direnv/direnv/tree/d6b6caacffba02169ed7f36dd5f972794ac40180); that's not where the file belongs.

So, please stop. If you've added it, please consider a PR to remove it so that future contributors can use the tools that make sense for them. 

Edit: [`@dtomvan`](https://toot.cat/@dtomvan) pointed out that this has been actively discussed in the issues for the direnv project here: https://github.com/direnv/direnv/issues/556, as well as by the Nix project here: https://github.com/NixOS/nixfmt/pull/118#discussion_r1718517899

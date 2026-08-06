---
title: How I Jujutsu Bookmark Advance
slug: how-i-jujutsu-bookmark-advance
date: 2026-08-06T08:18:23.034837
tags: 
- jujutsu
- version-control
- tips
category: tools
author: Chris Rose
email: offline@offby1.net
status: published
summary: A quick bit on how I've made use of jj bookmark advance 
toot: https://wandering.shop/@offby1/117049339064455680
---

`jj bookmark advance` is a relatively new feature[ref]as of version 0.39[/ref] of [Jujutsu](https://github.com/jj-vcs/jj) that replaced the nearly ubiquitous `jj tug` alias that moved bookmarks to the "tip" of their respective commit DAGs.

The way it works is by moving the matched bookmarks to the revset specified in `revsets.bookmark-advance-to`, which by default is `@` -- ie, the current active commit.

I find that to be unhelpful because I've often got unpushable commits in my history, so mine is a bit more involved:

```toml
[revsets]
bookmark-advance-to = "closest_pushable(@)"

[revset-aliases]
'closest_pushable(to)' = 'heads(::to & mutable() & ~denylist() & ~description(exact:"") & (~empty() | merges()))'

'denylist()' = 'wip() | private()'
'wip()' = 'description(glob:"wip:*") | description(glob:"WIP:*")'
'private()' = "description(glob:'private:*')"
```

Collectively, this gives me a configuration where bookmarks advance to where it is "safe" to do so, rather than to the current commit. It means that `jj git push` doesn't try to push a commit that is otherwise denied by my push policies (because I have `git.private-commits` set to `denylist()` as well).

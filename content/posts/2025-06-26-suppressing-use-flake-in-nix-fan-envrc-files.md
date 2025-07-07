Title: Suppressing "use flake" in nix fan .envrc files
Slug: suppressing-use-flake-in-nix-fan-envrc-files
Date: 2025-06-26T20:51:14.762573
Tags: petpeeve, direnv, nix
Category: tools
Author: Chris Rose
Email: offline@offby1.net
Status: published
Toot: https://wandering.shop/@offby1/114753269522469030
Summary: Are you annoyed by direnv-using nix fans committing .envrc files with "use flake" in them? Is this an overly specific complaint turned into a blog post? Is there a solution to your very specific problem within? 

This'll be short, but sweet[ref]Actually, pretty salty[/ref]:

1. I often check out open source projects with the intent to read their code or sometimes contribute small changes.
2. I use direnv, which uses a `.envrc` in the root directory to configure the environment
3. I do _not_ use nix.
4. Nix fans are apparently fond of putting `use flake` in their `.envrc` files.
5. Nix fans are, also, fond of _committing this file to git_.

It's that last bit that really chafes me; I don't use nix, and I'm not likely ever to -- it's really invasive to install on macOS, and never really clicked for me. When these `.envrc` files are present, I get the lovely experience of seeing one of these two outputs every time I chdir to a package written by one of these nix fans:

```shellsession
$ cd some-project
direnv: error /Users/offby1/projects/some-project/.envrc is blocked. Run `direnv allow` to approve its content
```

Or, if I allow it:

```shellsession
$ cd some-project
$ direnv allow
direnv: loading ~/projects/some-project/.envrc
direnv: using flake
environment:1270: nix: command not found
```

Both of those kinda suck. Moreover, if I have my own local environment I want to load, I'm now SOL because they checked one in.

So, first up, if you do that, [*stop*](https://wandering.shop/@offby1/114753269522469030).

But, since they likely won't do so, here's something as a direnv user you can do to mitigate it; create your own `use_flake()` function in `~/.config/direnv/direnvrc`:

```shell
use_flake() {
    log_status "No, I don't think I will 'use flake', thank you!"
    
    source_env_if_exists .envrc.local
}
```

That will supersede the direnv stdlib function, first, but also it will let you put a .envrc.local file into the same directory, which you can use to customize your own development environment.

So, there, a peeve and a solution.

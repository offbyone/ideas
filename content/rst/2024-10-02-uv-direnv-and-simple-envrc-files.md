Title: uv, direnv, and simple .envrc files
Slug: uv-direnv-and-simple-envrc-files
Date: 2024-10-02T00:05:01.102701
Tags: uv, python, direnv, tool-sharpening
Category: tools
Author: Chris Rose
Email: offline@offby1.net
Toot:
Status: published
Summary: Easily using uv, direnv, and minimal, consistent .envrc files

I have adopted [`uv`](https://astral.sh/uv/) for a lot of Python development. I'm also a heavy user of [`direnv`](https://direnv.net/), which I like as a tool for setting up project-specific environments. 

Much like [Hynek describes](https://www.youtube.com/watch?v=8UuW8o4bHbw), I've found `uv sync` to be fast enough to put into the chdir path for new directories. Here's how I'm doing it.

## Direnv Libraries

First, it turns out you can pretty easily define custom direnv functions like the built-in ones (`layout python`, etc...). You do this by adding functions to `~/.config/direnv/direnvrc` or in `~/.config/direnv/lib/` as shell scripts. I use this extensively to make my `.envrc` files easier to maintain and smaller. Now that I'm using `uv` here is my default for python:

```bash
function use_standard-python() {
    source_up_if_exists

    dotenv_if_exists

    source_env_if_exists .envrc.local

    use venv

    uv sync
}
```

## What does that even mean?

Let me explain each of these commands and why they are there:

* `source_up_if_exists` -- this [direnv stdlib](https://direnv.net/man/direnv-stdlib.1.html) function is here because I often group my projects into directories with common configuration. For example, when working on [Chicon 8](https://chicon.org), I had a top level `.envrc` that set up the AWS configuration to support deploying [Wellington](https://github.com/ChicagoWorldcon/wellington) and the Chicon 8 website. This searches up til it finds a `.envrc` in a higher directory, and uses that. `source_up` is the noisier, less-adaptable sibling.

* `dotenv_if_exists` -- this loads `.env` from the current working directory. 12-factor apps often have environment-driven configuration, and `docker compose` uses them relatively seamlessly as well. Doing this makes it easier to run commands from my shell that behave like my development environment. 

* `source_env_if_exists .envrc.local` -- sometimes you need more complex functionality in a project than just environment variables. Having this hear lets me use `.envrc.local` for that. This comes after `.env` because sometimes you want to change those values. 

* `use venv` -- this is a function that activates the project `.venv` (creating it if needed); I'm old and set in my ways, and I prefer `. .venv/bin/activate.fish` in my shell to the more newfangled "prefix it with a runner" mode.

* `uv sync` -- this is a super fast, "install my development and main dependencies" command. This was way, way too slow with `pip`, `pip-tools`, `poetry`, `pdm`, or `hatch`, but with `uv`, I don't mind having this in my `.envrc`

## Using it in a sentence

With this set up in direnv's configuration, all I need in my `.envrc` file is this:

```bash
use standard-python
```

I've been using this pattern for a while now; it lets me upgrade how I do default Python setups, with project specific settings, easily.

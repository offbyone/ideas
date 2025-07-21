Title: direnv and pip-tools together
slug: direnv-and-pip-tools-together
date: 2020-06-16T07:15:02.430301
category: tools
tags: programming, direnv, python, pip-tools, automation
author: Chris Rose
email: offline@offby1.net
status: published
summary: A relatively simple way to automate locking your pip-tools requirements using direnv

I have been experimenting with using [pip-tools](https://github.com/jazzband/pip-tools/) to manage my python project dependencies. If you're not familiar with it, I encourage you to read Hynek Schlawack's excellent [introduction to dependency management in Python](https://hynek.me/articles/python-app-deps-2018/) which introduces it and offers some comparisons to other alternatives like Poetry and Pipenv.

The simple explanation, though, is that pip-tools offers two commands: `pip-compile` and `pip-sync` that work to keep a virtualenv's dependencies both reproducible and in sync with the expressed requirements. This is done by having the developer edit a `requirements.in` file, which is compiled into `requirements.txt`, and then synced into the project virtualenv.

At the same time as I've been on this kick, I've also been trying out [direnv](https://direnv.net), which I am *very* late to the party on. Direnv is a tool for managing per-directory (or directory tree) environment variables, evaluating a bash script in a limited interpreter to set custom environment variables in fish, zsh, or bash shells. One of its highlights is its useful stdlib, including a great python + virtualenv integration:

``` bash
layout python python3.9
```

This simple command creates a virtualenv using Python 3.9 in the project directory, and automatically activates and deactivates it as you enter/exit. Afterwards, you can install `pip-tools` in that virtualenv the old fashioned way:

``` console
$ pip install pip-tools
... some output here
Successfully installed pip-20.1.1 pip-tools-5.2.1
```

Now, if I wanted to add a dependency, I would simply insert it into my `requirements.in` file:

``` ini
click
```

And pip-compile/sync:

``` console
$ pip-compile requirements.in
... prints out the contents of requirements.txt, and writes it
click==7.1.2              # via -r requirements.in
$ pip-sync requirements.txt
... some output
Successfully installed click-7.1.2
```

This is pretty easy\... but what if you could skip all of these manual steps? Direnv has a way: custom hooks in `~/.config/direnv/direnvrc` that you can reference in your `.envrc` files. Here's how I manage my pip-compile automation:

``` bash
function use_pip-tools() {
    requirements_file=${1:?"a requirements file must be provided as the first argument"}
    shift
    local has_pip=0
    if has pip; then
        if [[ $(which pip) = $PWD/* ]]; then
            has_pip=1
        fi
    fi
    if [ $has_pip -eq 0 ]; then
        echo "[use pip-tools] No pip installed via layout; try layout pyenv or layout python"
        return 1
    fi

    if ! test -f $requirements_file; then
        echo "[use pip-tools] No requirements file $requirements_file"
        return 1
    fi

    if ! has pip-compile; then
        echo "[use pip-tools] pip-tools missing; installing"
        pip install pip-tools
    fi

    requirements_txt=$(echo "$requirements_file" | cut -f 1 -d '.').txt
    if [ $requirements_file -nt $requirements_txt ]; then
        echo "[use pip-tools] resyncing requirements"
        pip-compile "$@" $requirements_file
        pip-sync $requirements_txt
    fi

    watch_file $requirements_file
}
```

And then, I just have to enable this in my `.envrc`:

``` bash
layout python python3.9
use pip-tools requirements.in
```

Now, when I change my requirements file, I get automatic pip-compilation:

``` console
$ echo requests >> requirements.in
direnv: loading ~/tmp/direnv-piptools/.envrc
direnv: using pip-tools requirements.in
[use pip-tools] resyncing requirements
...
requests==2.23.0          # via -r requirements.in
...
Successfully installed certifi-2020.4.5.2 chardet-3.0.4 idna-2.9 requests-2.23.0 urllib3-1.25.9
direnv: export +VIRTUAL_ENV ~PATH
```

And voila! Every time you update your `requirements.in` your virtualenv will resync automatically. Also, any time your `requirements.in` file is newer than the compiled one, it'll re-run this too.

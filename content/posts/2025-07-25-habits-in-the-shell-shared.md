Title: Habits in the Shell, shared
Slug: habits-in-the-shell-shared
Date: 2025-07-25T09:26:31.883943
Tags: shell, chezmoi, habits, til
Category: tools
Author: Chris Rose
Email: offline@offby1.net
Status: published
Summary: Summarize this

[A post I saw today](https://www.judy.co.uk/blog/using-fortune-to-reinforce-habits/) about "using `fortune` to remind me of the shell tools I have installed, instead of the old ones I use by reflex" got me really excited by the idea of the reminders. 

I adopted the basic idea immediately -- putting the habits in `~/.local/share/habits/` and adding the fortune to my [fish shell](https://fishshell.com/) greeting. It was great!

But...

I wanted it to be shared between my machines, instead of being per-machine. That meant I needed to do some more work to tie it into [chezmoi](https://chezmoi.io/). This post covers that. I'll be using chezmoi's [`run_onchange_` script support](https://www.chezmoi.io/user-guide/use-scripts-to-perform-actions/#clear-the-state-of-all-run_onchange_-and-run_once_-scripts), to adapt Mark's idea.

Here's what I have in chezmoi's `dot_local/share/habits/` directory:

```
$ ll
.rw-r--r--@ 670 offby1 25 Jul 08:37 0_habits
.rw-r--r--@  68 offby1 25 Jul 08:37 README.md
.rw-r--r--@ 230 offby1 25 Jul 08:48 run_onchange_compile_habits.sh.tmpl
```

The only interesting thing in there is the onchange script:

```{ .shell }
#!/bin/bash
set -eu -o pipefail

# Habits hash: {{ include "private_dot_local/share/habits/0_habits" | sha256sum }}

strfile 0_habits habits.dat
# the habits file must be named "habits" for fortune to
# find it
mv 0_habits habits
```

I had to work around chezmoi's ordering, which wouldn't write the `habits` file until after the on-change script was run. That meant that habits didn't update on change, only after the change. That's why `0_habits` instead of `habits`. Second, The file has to be moved into `habits` because the fortune index file needs the name to match.

I also added a script to add new habits, so I could do so easily; it renders as `,add-habit`[ref]Naturally, you also [start all of your commands with a comma](https://rhodesmill.org/brandon/2009/commands-with-comma/), right?[/ref] on my `PATH`:

```{ .shell }
#!/bin/bash

HABIT_DIR=$HOME/.local/share/habits
HABIT_FILE=$HABIT_DIR/0_habits

# we assume a habit file exists.

echo "%" >>$HABIT_FILE
echo "$@" >>$HABIT_FILE

cd $HABIT_DIR
just compile-habits
```

<details>
<summary>If you're curious, this is the full diff I applied to my dotfiles to enable this functionality, including the shell integrations[ref]and a bootstrap set of habits from Hynek. Thanks![/ref]:</summary>
```{ .patch }
diff --git a/dot_bashrc.tmpl b/dot_bashrc.tmpl
index f6e9b806a2..c3d545c02d 100644
--- a/dot_bashrc.tmpl
+++ b/dot_bashrc.tmpl
@@ -19,4 +19,7 @@
 [[ $(type -P atuin) ]] && eval "$(atuin init --disable-up-arrow bash)"
 
 [[ $(type -P zoxide) ]] && eval "$(zoxide init bash)"
+
+fortune ~/.local/share/habits | lolcrab | boxes -d parchment
+
 {{- end }}
diff --git a/dot_config/private_fish/functions/fish_greeting.fish b/dot_config/private_fish/functions/fish_greeting.fish
new file mode 100644
index 0000000000..d536eff984
--- /dev/null
+++ b/dot_config/private_fish/functions/fish_greeting.fish
@@ -0,0 +1,3 @@
+function fish_greeting
+  fortune ~/.local/share/habits | lolcrab | boxes -d parchment
+end
diff --git a/dot_zshrc.tmpl b/dot_zshrc.tmpl
index 376afb6368..018de28db1 100644
--- a/dot_zshrc.tmpl
+++ b/dot_zshrc.tmpl
@@ -50,3 +50,5 @@
 type -p atuin &>/dev/null && eval "$(atuin init --disable-up-arrow zsh)"
 
 type -p zoxide &>/dev/null && eval "$(zoxide init zsh)"
+
+fortune ~/.local/share/habits | lolcrab | boxes -d parchment
diff --git a/private_dot_local/bin/executable_,add-habit b/private_dot_local/bin/executable_,add-habit
new file mode 100644
index 0000000000..60c6165545
--- /dev/null
+++ b/private_dot_local/bin/executable_,add-habit
@@ -0,0 +1,16 @@
+#!/bin/bash
+
+HABIT_DIR=$HOME/.local/share/habits
+HABIT_FILE=$HABIT_DIR/0_habits
+
+# we assume a habit file exists.
+
+echo "%" >>$HABIT_FILE
+echo "$@" >>$HABIT_FILE
+
+cd $HABIT_DIR
+
+strfile 0_habits habits.dat
+# the habits file must be named "habits" for fortune to
+# find it
+mv 0_habits habits
diff --git a/private_dot_local/share/habits/0_habits b/private_dot_local/share/habits/0_habits
new file mode 100644
index 0000000000..7bb7c7b2b0
--- /dev/null
+++ b/private_dot_local/share/habits/0_habits
@@ -0,0 +1,27 @@
+make sure to add habits you like to ~/.local/share/chezmoi/private_dot_local/share/habits/habits.
+%
+Still using man? Try using `tldr` first!
+%
+Don't forget about `hexyl`! A handy binary file viewer.
+%
+`trippy` (started as `trip`) is the new mtr/traceroute.
+%
+`bandwhich` shows network usage.
+%
+`rlwrap` adds readline superpowers to commands that lack them.
+%
+`tre` is a nicer tree.
+%
+`dust` and `gdu-go` are nicer du replacements.
+%
+`hyperfine` for CLI benchmarking, `oha` for http.
+%
+`duf` instead of df (disk full, NOT disk usage).
+%
+`hurl` to stress/test HTTP.
+%
+`hwatch` to repeatedly run commands and compare output.
+%
+`dog` for better DNS.
+%
+`tokei` to count LoC.
diff --git a/private_dot_local/share/habits/README.md b/private_dot_local/share/habits/README.md
new file mode 100644
index 0000000000..b06f2fcc8d
--- /dev/null
+++ b/private_dot_local/share/habits/README.md
@@ -0,0 +1,1 @@
+We use `0_habits` because chezmoi is ordering sensitive, damn it...
diff --git a/private_dot_local/share/habits/run_onchange_compile_habits.sh.tmpl b/private_dot_local/share/habits/run_onchange_compile_habits.sh.tmpl
new file mode 100644
index 0000000000..4ad17ea927
--- /dev/null
+++ b/private_dot_local/share/habits/run_onchange_compile_habits.sh.tmpl
@@ -0,0 +1,9 @@
+#!/bin/bash
+set -eu -o pipefail
+
+# Habits hash: {{ include "private_dot_local/share/habits/0_habits" | sha256sum }}
+
+strfile 0_habits habits.dat
+# the habits file must be named "habits" for fortune to
+# find it
+mv 0_habits habits
```
</details>

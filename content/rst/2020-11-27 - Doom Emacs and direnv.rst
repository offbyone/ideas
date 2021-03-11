Doom Emacs and direnv
########################################################################

.. role:: raw-html(raw)
    :format: html

:slug: doom-emacs-and-direnv
:date: 2020-11-27T10:24:22.509234
:category: tools
:tags: emacs, direnv
:author: Chris Rose
:email: offline@offby1.net
:excerpt: Solving an issue arising from an interaction between Doom Emacs and direnv
:status: published

I use both `Doom Emacs`_ and `Direnv`_ a lot, and I discovered -- and with the author of Doom's assistance, solved -- an peculiar issue arising from the interaction of the two.

Doom defines a :code:`doom sync` command whose job it is to update the compiled elisp for packages, but also to update the environment used by emacs, including its PATH, by writing out the full current environment to a local cache. That allows Emacs to be independent of the shell invoking it.

Direnv customizes your shell environment based on your current working directory.

When both of these are in play, though, running :code:`doom sync` can have interesting effects, since the direnv state will be retained when generating your synced environment file.

So, I took advantage of a hidden, but valuable, feature in Doom's cli: Env pre-hooks. I added a :code:`cli.el` file to the :code:`~/.doom.d` configuration directory, and in that file I added a hook to check for direnv and prevent sync if running in a direnv:

.. code-block:: elisp
   
  (add-hook! 'doom-sync-pre-hook
    (or (not (getenv "DIRENV_DIR"))
        doom-auto-accept
        (y-or-n-p "doom env update: Direnv detected! Continue anyway?")
        (user-error "Aborted")))

This helps me avoid overwriting my neutral environment with project-specific content.

I haven't managed to identify a full set of available hooks, but I know that :code:`doom-sync-pre-hook` and :code:`doom-env-pre-hook` exist at a minimum.
    
.. _`Doom Emacs`: https://github.com/hlissner/doom-emacs
.. _`Direnv`: https://direnv.net

Title: On parsing
date: 2004-03-02 19:48
author: offby1
category: Projects
tags: projects
slug: on-parsing
status: draft

I generally avoid posting on this sort of thing, because people's eyes tend to glaze over when i start talking about it, but i'm just getting some serious progress done on my first "parser":http://en.wikipedia.org/wiki/Parser and i wanted to brag a bit about it.

What i'm doing, i suppose i should explain, is making an editor for "vCards":http://www.imc.org/pdi/vcardoverview.html \-- specifically, for use with my iPod's contact list. It occurred to me as i was looking for tools that there are really very few good vCard editors out there, for windows or any other platform, and so i took it upon myself to write one of my own.

Basically, i'm at the point where i have to build a working "AST":http://en.wikipedia.org/wiki/Abstract_syntax_tree for it, which is pretty much all that separates me from having a full job of it. Progress is slow, since the "tool":http://www.antlr.org/ i'm using assumes knowledge that i just don't have yet, and the documentation really reflects that. But the user community is helpful and patient, and i'm making steady progress.

In theory this was supposed to morph into a group project, but that has kind of failed to materialize. So, i'm going to get it to a rudimentary v0.5 level, release it into the wild, and see if anyone uses it and files bug reports against it. Hopefully we'll see something come of it.

I'll keep people posted, especially once i have a pretty GUI to show off in screen shots.

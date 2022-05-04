A Rant on Coding and Quality
############################
:date: 2007-03-27 10:11
:author: offby1
:category: Rants
:tags: good design, incompetence, model-view-controller, rants, school, software engineering, vitriol
:slug: a-rant-on-coding-and-quality
:status: draft

I am, as Char will no doubt agree, occasionally a bit on the negative
side. This isn't always a good thing; I need to learn to tone down my
vitriol in situations in which it does not advance my needs, and in
those in which it is not necessary or constructive.

There are times, however, that merit a vigorous negative response.

I'm taking two project courses in school this semester; Cmput 414, which
is a graphics and multimedia course with a heavy algorithmic programming
component, and Cmput 401, a software engineering course and the focus of
this rant.

Software Engineering is, according to
[Wikipedia](http://en.wikipedia.org/wiki/Software\_engineering), "is the
application of a systematic, disciplined, quantifiable approach to the
development, operation, and maintenance of software." Among other
things, it requires the application of good design practices to the
development of code, and following beneficial design standards.

So, I have to ask, why is it that people taking this fucking course
cannot do something as basic as grok that it is \_fundamentally bad
practice to add public methods to hidden implementing classes instead of
using the goddamned design?!\_ I spent three days nailing down, and
countless hours tuning up, the data model for our project application,
only to have one of my fellow team members simply come along and,
instead of \_reading the goddamned documentation\_, which I provided as
a first step, add new hooks into the mechanism, just to get at the
information in a way that is not only wrong, but disables some nice and
(I thought) needed functionality.

I have spent the last hour looking over his code, marveling at the
glorious unification of layers that, according to [good design
practices](http://en.wikipedia.org/wiki/Model-view-controller), should
ever remain separate -- the intermingling of UI code and logic that
\_I'd already written elsewhere, better\_ was a real high point for me.

Gods.

I cannot wait to get back to full time work with people who know
\_more\_ than I do, so that instead of raging at the pathetic efforts of
people whose skills are not even up to the level of an academic
programmer, I can instead find faults with my own approaches, be told
that I'm doing it wrong, and learn how to do it \_better\_.

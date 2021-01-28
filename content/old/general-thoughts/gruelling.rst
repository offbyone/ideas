Gruelling
#########
:date: 2003-11-18 22:54
:author: offby1
:category: General Thoughts
:tags: school
:slug: gruelling
:status: draft

Wow. That was a pain.

About a week and a half ago, we were given what seemed to be a
relatively straightforward assignment in CMPT229. Nothing fancy, just
implement a [doubly linked
list](http://www.instantweb.com/D/dictionary/foldoc.cgi?doubly+linked+list)
in assembler.

This would be easier, but then there's the whole \_assembler\_ part of
that statement.

Assembler is a form of low-level programming language that, for the
purposes of this class, looks like this:

.. raw:: html

   <p>

| getPrevious\_loop:
| sub $s0, 1
| bltz $s0, getPrevious\_retzero
| move $a0, $s1
| jal getElementData
| beq $v0, $s2, getPrevious\_found
| move $a0, $s1
| jal getNextElement # get the next element
| move $s1, $v0
| j getPrevious\_loop

.. raw:: html

   </pre>

So, anyway, i just spent about five more hours than i ever expected to
hammering away at that. And i got it working! It's a hideous kludge, but
it works. And it might even make some kind of sense to someone else
reading it.

But that, i doubt :)

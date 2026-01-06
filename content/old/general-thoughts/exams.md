---
title: Exams
slug: exams
date: 2006-04-20 07:05
tags:
- school
- simon
author: offby1
status: draft
---
Well, exa*m*, anyway.

I just polished off the final exam for Cmput 313, a low-level networking course. (aside: I mistyped "course" as "curse." Is there such a thing as a slip of the fingers? Very freudian, that, on two levels.) It was a bit of a challenge, but I think the hardest part was maintaining my interest in the face of my disappointment about the content of the course.

This post is a bit in the vein of the ultra-obtuse posts that Simon makes from time to time, so bear with me. I'm a bit new at this ;)

There's a conceptual model of networks which has them divided into 7 layers. The 7 layers are organized a lot like this:

:::{figure} /images/2006-04-01/osi_model.jpg
:alt: OSI 7-layer model
:width: 372px

*[OSI 7-layer model](http://en.wikipedia.org/wiki/OSI_model)*
:::

The image is linked to the obligatory Wikipedia article for those who are a bit more interested.

Broadly speaking, most networks follow this model fairly closely for layers 1-4, and tend to blur layers 5-7 into one.

The problem with the course was that I am interested in layer 7, and to a lesser extent layer 6. The course's focus, however, was on the low-level protocols that go on in layers 1-4. I'm not saying that those are not interesting in their own rights -- I learned a lot, and there certainly is a lot *to* learn on the subject... It's just that it doesn't interest me directly.

It is kind of neat, in the end. You'd be amazed at some of the hoops the lower layers of this model jump through to keep your data accurate. Down at layer 1, there's an amazing amount of complexity just in encoding a single 1 or 0 for transmission. In reality, for each of these bits several machine-layer bits might be sent to ensure that (just for example) the boundary between two successive bits can be determined.

Layer 2 has some interesting statistical behaviour determining what happens when two stations try to use one resource at the same time. That's been the basis of most of my assignments, this term.

L3 is where IP sits. For those not in the know, IP is the backbone of TCP/IP, which is the way computers on the internet communicate.

And so on...

If your eyes are glazing over, don't feel bad -- that's my whole complaint with the course! ;)
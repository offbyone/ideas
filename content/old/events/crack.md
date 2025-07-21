Title: Crack
date: 2005-02-16 08:41
author: offby1
category: Events, General Thoughts, Internet
tags: events, intellectual property, internet, privacy
slug: crack
status: draft

Esoterica? Pah!

Word has come down from a research team (via a [major authority](<http://www.amazon.com/exec/obidos/tg/detail/-/0471117099/>) on cryptography) that the [SHA-1 hash algorithm has been broken]([http://www.schneier.com/blog/archives/2005/02/sha1_broken.html](http://www.schneier.com/blog/archives/2005/02/sha1_broken.html)) (discussed [here]([http://www.technorati.com/cosmos/search.html?rank=&url=http%3A%2F%2Fwww.schneier.com%2Fblog%2Farchives%2F2005%2F02%2Fsha1_broken.html](http://www.technorati.com/cosmos/search.html?rank=&url=http%3A%2F%2Fwww.schneier.com%2Fblog%2Farchives%2F2005%2F02%2Fsha1_broken.html)) and [here](<http://it.slashdot.org/article.pl?sid=05/02/16/0146218&tid=93&tid=172&tid=218>))

This is a bit tough to grok if you're not a crypto-nerd, but essentially what this means is that one of the fundamental ways of _signing_ (not encrypting, that's a whole different ball of wax) a document cryptographically has been compromized. This isn't immediately fatal, but it does bring computation of these hashes into the realm of possibility sooner rather than later. Essentially, the team conducting the research has cut a factor of 2\^11 (2048, for the binary-impaired) off of the time required to force a [hash collision]([http://en.wikipedia.org/wiki/Hash_collision](http://en.wikipedia.org/wiki/Hash_collision)) (NSFNG(Not Safe For Non-Geeks)). This cuts the work involved down from approximately 1208925819614629174706176 attempts to 590295810358705651712. Scary, isn't it?

What this means, basically, is it is plausibly possible for an attacker with the computer resources of the NSA or a major world-class computing centre to get someone to sign a document, then substitute another one for it that will pass as having been signed legitimately. This has fairly broad implications in an age where the validity of electronic evidence is [being questioned](<http://www.uscourts.gov/rules/comment2005/CVAug04.pdf>) (pdf).

Still, I guess it's not that big of a deal. Something better will [come up](http://planeta.terra.com.br/informatica/paulobarreto/hflounge.html), I'm sure.

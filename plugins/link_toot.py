"""Link a Fediverse toot from a post

Setting a `Toot` property on the post, with `domain`, `username`, and `id` properties
can be turned into a toot reference, which can be used in themes.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from pelican import signals
from pelican.contents import Content

log = logging.getLogger("link_toot")

@dataclass
class Toot:
    domain: str
    username: str
    id: str

def parse_toot(content: Content):
    if not "toot" in content.metadata:
        return

    toot_str = content.metadata["toot"]


    try:
        toot_parts = [p.strip() for p in toot_str.split(",")]
        toot_keys = {k.strip(): v.strip() for k, v in [p.split("=") for p in toot_parts]}
    except ValueError:
        # maybe the toot was a URL?
        parsed = urlparse(toot_str)
        if parsed.scheme != "https":
            # not a valid URL
            log.warning(f"Invalid toot property on content {content}: {toot_str}")
            del content.metadata["toot"]
            del content.toot
            return

        toot_path = Path(parsed.path)
        toot_keys = {
            "domain": parsed.netloc,
            "username": toot_path.parts[1],
            "id": toot_path.stem,
        }

    try:
        content.toot = Toot(
            domain=toot_keys["domain"],
            username=toot_keys["username"],
            id=toot_keys["id"],
        )
        log.debug(f"Added toot metadata {content.toot} to {content}")

    except KeyError:
        log.warning(f"Incomplete toot property on content {content}: {toot_str}")
        del content.metadata["toot"]
        del content.toot
        return

def register():
    signals.content_object_init.connect(parse_toot)

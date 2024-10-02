import datetime
import os
import shutil
import sys
from pathlib import Path
from textwrap import dedent

import docutils.frontend
import docutils.nodes
import docutils.parsers.rst
import docutils.utils
from invoke import call, task
from pelican.server import ComplexHTTPRequestHandler, RootedHTTPServer
from pelican.settings import DEFAULT_CONFIG, get_settings_from_file
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from slugify import slugify


def parse_rst(text: str) -> docutils.nodes.document:
    parser = docutils.parsers.rst.Parser()
    components = (docutils.parsers.rst.Parser,)
    settings = docutils.frontend.OptionParser(
        components=components
    ).get_default_values()
    document = docutils.utils.new_document("<rst-doc>", settings=settings)
    parser.parse(text, document)
    return document


SETTINGS_FILE_BASE = "pelicanconf.py"
SETTINGS = {}
SETTINGS.update(DEFAULT_CONFIG)
LOCAL_SETTINGS = get_settings_from_file(SETTINGS_FILE_BASE)
SETTINGS.update(LOCAL_SETTINGS)

CONFIG = {
    "settings_base": SETTINGS_FILE_BASE,
    "settings_publish": "publishconf.py",
    # Output path. Can be absolute or relative to tasks.py. Default: 'output'
    "deploy_path": SETTINGS["OUTPUT_PATH"],
    # Github Pages configuration
    "github_pages_branch": "master",
    "commit_message": "'Publish site on {}'".format(datetime.date.today().isoformat()),
    # Port for `serve`
    "port": 8000,
    "s3_bucket": "ideas.offby1.net",
    "cloudfrount_distribution_id": "E3HG7SIR4ZZAS1",
}

console = Console()


@task
def clean(c):
    """Remove generated files"""
    if os.path.isdir(CONFIG["deploy_path"]):
        shutil.rmtree(CONFIG["deploy_path"])
        os.makedirs(CONFIG["deploy_path"])


@task
def build(c, production=True, delete=True, output_path=None):
    """Build the site"""
    settings = CONFIG["settings_publish"] if production else CONFIG["settings_base"]
    flags = []
    if delete:
        flags.append("-d")
    if output_path:
        flags.append("-o")
        flags.append(output_path)
    c.run(f"pelican {' '.join(flags)} -s {settings}")


@task(pre=[call(build, production=False, delete=True)])
def rebuild(c):
    """`build` with the delete switch"""
    ...


@task
def regenerate(c):
    """Automatically regenerate site upon file modification"""
    c.run("pelican -r -s {settings_base}".format(**CONFIG))


@task(call(build, production=False))
def serve(c):
    """Serve site at http://localhost:$PORT/ (default port is 8000)"""

    class AddressReuseTCPServer(RootedHTTPServer):
        allow_reuse_address = True

    server = AddressReuseTCPServer(
        CONFIG["deploy_path"], ("", CONFIG["port"]), ComplexHTTPRequestHandler
    )

    sys.stderr.write("Serving on port {port} ...\n".format(**CONFIG))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


@task
def devserver(c):
    c.run(f"pelican -D -l -r --port {CONFIG['port']}")


@task(build)
def preview(c):
    """Build production version of site"""
    ...


@task
def livereload(c):
    """Automatically reload browser tab upon file modification."""
    from livereload import Server

    build(c)
    server = Server()
    # Watch the base settings file
    server.watch(CONFIG["settings_base"], lambda: build(c))
    # Watch content source files
    content_file_extensions = [".md", ".rst"]
    for extension in content_file_extensions:
        content_blob = "{0}/**/*{1}".format(SETTINGS["PATH"], extension)
        server.watch(content_blob, lambda: build(c))
    # Watch the theme's templates and static assets
    theme_path = SETTINGS["THEME"]
    server.watch("{}/templates/*.html".format(theme_path), lambda: build(c))
    static_file_extensions = [".css", ".js"]
    for extension in static_file_extensions:
        static_file = "{0}/static/**/*{1}".format(theme_path, extension)
        server.watch(static_file, lambda: build(c))
    # Serve output path on configured port
    server.serve(port=CONFIG["port"], root=CONFIG["deploy_path"])


@task
def prepare_fonts(c):
    c.run(
        "rsync -pthrvz node_modules/@fortawesome/fontawesome-free/webfonts/ themes/offby1/static/webfonts/"
    )


@task(pre=[prepare_fonts])
def site(c):
    """generate using production settings"""
    c.run(
        f"pelican {SETTINGS['PATH']} -o {CONFIG['deploy_path']} -s {CONFIG['settings_publish']}"
    )


@task
def upload(c):
    """Upload the site to the production S3 bucket"""
    c.run(f"aws s3 sync --delete {CONFIG['deploy_path']} s3://{CONFIG['s3_bucket']}")


@task
def invalidate(c):
    c.run(
        f"aws cloudfront create-invalidation --distribution-id {CONFIG['cloudfrount_distribution_id']} --paths '/*'"
    )


@task(pre=[site, upload], post=[invalidate])
def publish(c):
    """Runs the `site` and `upload` tasks, and then invalidates the CF distribution so the site goes live."""
    ...


@task
def compile_deps(c, upgrade=False):
    """Compile the pip deps to lock them"""
    if upgrade:
        c.run(
            "pip-compile -U --no-emit-trusted-host --no-emit-index-url requirements.in"
        )
        return

    if (
        Path("requirements.txt").stat().st_mtime
        < Path("requirements.in").stat().st_mtime
    ):
        c.run("pip-compile --no-emit-trusted-host --no-emit-index-url requirements.in")


@task(compile_deps)
def deps(c):
    """Sync the dependencies into the working virtualenv"""
    c.run("pip-sync requirements.txt")


@task(post=[deps], pre=[call(compile_deps, upgrade=True)])
def upgrade(c):
    """Upgrade and sync all dependencies"""


@task
def new_post(c, title=None, post_type="md"):
    """Create a blank new post in SETTINGS['PATH']"""
    if title is not None:
        filename_title_string = f"-{slugify(title)}"
        title_string = title
    else:
        console.print("[bold magenta]Please enter the title:[/bold magenta]")
        title = Prompt.ask("Title", default="New Post")
        filename_title_string = f"-{slugify(title)}"
        title_string = title
    new_post_path = (
        Path(SETTINGS["PATH"])
        / "rst"
        / f"{datetime.date.today().isoformat()}{filename_title_string}.{post_type}"
    )

    if post_type == "rst":
        title_bar = "#" * len(title_string)
        new_post_path.write_text(
            dedent(
                f"""\
        {title_string}
        {title_bar}

        .. role:: raw-html(raw)
            :format: html

        :slug: {slugify(title_string)}
        :date: {datetime.datetime.now().isoformat()}
        :category: CATEGORY
        :tags:
        :author: Chris Rose
        :email: offline@offby1.net
        :summary:

        A New Post
        """
            )
        )
    else:
        new_post_path.write_text(
            dedent(
                f"""\
        Title: {title_string}
        Slug: { slugify(title_string) }
        Date: {datetime.datetime.now().isoformat()}
        Tags:
        Category: CATEGORY
        Author: Chris Rose
        Email: offline@offby1.net
        Status: draft
        Summary: Summarize this
        """
            )
        )
    c.run(f"git add '{new_post_path}'")


class Visitor(docutils.nodes.NodeVisitor):
    def __init__(self, doc):
        super().__init__(doc)

        self.fields = {}

    def visit_field(self, field: docutils.nodes.Node) -> None:
        self.fields[field.children[0].astext()] = field.children[1].astext()

    def unknown_visit(self, node: docutils.nodes.Node) -> None:
        # print(node.pformat())
        ...


def get_tags(doc: docutils.nodes.document) -> list[str]:
    v = Visitor(doc)
    doc.walk(v)
    return [t.strip() for t in v.fields["tags"].split(",") if t.strip()]


def get_category(doc: docutils.nodes.document) -> str:
    v = Visitor(doc)
    doc.walk(v)
    return v.fields["category"].strip()


def content_paths(relative="content/rst", extensions=(".rst",)):
    for root, _, files in os.walk(relative):
        for f in files:
            p = Path(root) / f
            if p.suffix not in extensions:
                continue
            yield p


@task
def list_tags(c):
    all_tags: dict[str : set[str]] = {}

    for p in content_paths():
        doc = parse_rst(p.read_text())
        tags = get_tags(doc)
        category = get_category(doc)
        for t in tags:
            all_tags.setdefault(t, set()).add(category)

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Tag")
    table.add_column("Categories")

    for t, v in sorted(all_tags.items()):
        table.add_row(t, ",".join(v))

    console.print(table)


@task
def list_categories(c):
    categories = []

    for p in content_paths():
        try:
            doc = parse_rst(p.read_text())
        except:  # noqa: E722
            print(f"Unable to parse categories from {p}")
            continue
        category = get_category(doc)
        if category not in categories:
            categories.append(category)

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Category")

    for c in sorted(categories):
        table.add_row(c)

    console.print(table)


@task
def photo_gallery_gen(c, location):
    """Create gallery metadata files."""
    fmt_path = Path(__file__).parent / "config"
    location = Path(location)
    with c.cd(location):
        exif_cmd = "exiftool -if '$filename !~ /\\.txt$$/'"
        if not (location / "exif.txt").exists():
            c.run(f"{exif_cmd} -f -p {fmt_path}/exif.fmt . | sort > exif.txt")
        else:
            console.print("[red]Skipping already present file [bold]exif.txt")

        if not (location / "captions.txt").exists():
            c.run(f"{exif_cmd} -f -p {fmt_path}/captions.fmt . | sort > captions.txt")
        else:
            console.print("[red]Skipping already present file [bold]captions.txt")


@task
def show_hcard(c, page="index.html"):
    """Show the current hcards for the index page"""
    import mf2py

    index = Path(__file__).parent / "output" / page

    with index.open(mode="r") as fh:
        mf = mf2py.parse(doc=fh)

    console.print(mf)

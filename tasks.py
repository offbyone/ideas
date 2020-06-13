import os
import shutil
import sys
import datetime
from textwrap import dedent
from pathlib import Path

from invoke import task, call
from pelican.server import ComplexHTTPRequestHandler, RootedHTTPServer
from pelican.settings import DEFAULT_CONFIG, get_settings_from_file
from slugify import slugify

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
    c.run(f"./develop_server.sh restart {CONFIG['port']}")


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
def site(c):
    """generate using production settings"""
    c.run(f"pelican {SETTINGS['PATH']} -o {CONFIG['deploy_path']} -s {CONFIG['settings_publish']}")
    if Path("extra").is_dir():
        c.run(f"rsync --exclude .DS_Store -pthrvz extra/ {CONFIG['deploy_path']}")


@task
def upload(c):
    """Upload the site to the production S3 bucket"""
    c.run(
        f"aws s3 sync --acl public-read --delete {CONFIG['deploy_path']} s3://{CONFIG['s3_bucket']}"
    )


@task
def invalidate(c):
    c.run(
        f"aws cloudfront create-invalidation --distribution-id {CONFIG['cloudfrount_distribution_id']} --paths '/*'"
    )


@task(pre=[site, upload], post=[invalidate])
def publish(c):
    ...


@task
def compile_deps(c, upgrade=False):
    """Compile the pip deps to lock them"""
    if upgrade:
        c.run("pip-compile -U --no-emit-trusted-host --no-emit-index-url requirements.in")
        return

    if Path("requirements.txt").stat().st_mtime < Path("requirements.in").stat().st_mtime:
        c.run("pip-compile --no-emit-trusted-host --no-emit-index-url requirements.in")


@task(compile_deps)
def deps(c):
    """Sync the dependencies into the working virtualenv"""
    c.run("pip-sync requirements.txt")


@task(post=[deps], pre=[call(compile_deps, upgrade=True)])
def upgrade(c):
    """Upgrade and sync all dependencies"""


@task
def new_post(c, title=None):
    """Create a blank new post in SETTINGS['PATH']"""
    if title is not None:
        filename_title_string = f" - {title}"
        title_string = title
    else:
        filename_title_string = ""
        title_string = "Post Title"
    new_post_path = (
        Path(SETTINGS["PATH"]) / "rst" / f"{datetime.date.today().isoformat()}{title_string}.rst"
    )

    new_post_path.write_text(
        dedent(
            """\
    {title_string}
    ########################################################################

    .. role:: raw-html(raw)
        :format: html

    :slug: {slugify(title_string)}
    :date: {datetime.datetime.now().isoformat()}
    :category: CATEGORY
    :tags: 
    :author: Chris Rose
    :email: offline@offby1.net
    :excerpt: 

    A New Post
    """
        )
    )
    c.run(f"git add {new_post_path}")

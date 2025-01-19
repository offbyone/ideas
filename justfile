set dotenv-load

default: pelican

pelican:
  uv run pelican

serve:
  uv run inv livereload

upload:
  uv run aws s3 sync \
    --delete \
    output \
    s3://ideas.offby1.net

invalidate:
  uv run aws cloudfront create-invalidation \
    --distribution-id E3HG7SIR4ZZAS1 \
    --paths "/*"

prepare_fonts:
  rsync -pthrvz \
    node_modules/@fortawesome/fontawesome-free/webfonts/ \
    themes/offby1/static/webfonts/

build settings="pelicanconf.py": prepare_fonts
  uv run pelican --fatal=errors -s {{settings}} -o output content

generate: (build "publishconf.py")

generate-dev: build

publish: generate upload invalidate

compile-deps:
  uv lock

update-deps:
  uv lock --upgrade

install-deps:
  uv sync

deps: compile-deps install-deps

plan:
    terraform plan -out plan.just

apply:
    terraform apply plan.just

new_post:
  uv run invoke new-post

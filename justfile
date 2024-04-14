set dotenv-load

default: pelican

pelican:
    pelican

serve:
    pelican --listen --autoreload

upload:
  aws s3 sync \
    --delete \
    output \
    s3://ideas.offby1.net

invalidate:
  aws cloudfront create-invalidation \
    --distribution-id E3HG7SIR4ZZAS1 \
    --paths "/*"

prepare_fonts:
  rsync -pthrvz \
    node_modules/@fortawesome/fontawesome-free/webfonts/ \
    themes/offby1/static/webfonts/

build settings="pelicanconf.py": prepare_fonts
  pelican --fatal=errors -s {{settings}} -o output content

generate: (build "publishconf.py")

generate-dev: build

publish: generate upload invalidate

compile-deps:
  pdm lock

update-deps:
  pdm update --update-all

install-deps:
  pdm install

deps: compile-deps install-deps

plan:
    terraform plan -out plan.just

apply:
    terraform apply plan.just

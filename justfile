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
    .venv/bin/pip-compile --no-emit-index-url \
      --no-emit-trusted-host \
      --unsafe-package=distribute \
      --unsafe-package=offby1-website \
      --unsafe-package=offby1.website \
      --unsafe-package=pip \
      --unsafe-package=setuptools \
      requirements.in

update-deps:
    .venv/bin/pip-compile --no-emit-index-url \
      --upgrade \
      --no-emit-trusted-host \
      --unsafe-package=distribute \
      --unsafe-package=offby1-website \
      --unsafe-package=offby1.website \
      --unsafe-package=pip \
      --unsafe-package=setuptools \
      requirements.in

install-deps:
    .venv/bin/pip-sync requirements.txt

deps: compile-deps install-deps

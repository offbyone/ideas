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

@build settings="pelicanconf.py":
  pelican -s {{settings}} -o output content

generate: (build "publishconf.py")
  pelican content -o output -s publishconf.py

generate-dev: build
  pelican content -o output -s pelicanconf.py

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

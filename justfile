set dotenv-load

default: pelican

pelican:
    pelican

serve:
    pelican --listen --autoreload

compile-deps:
    .venv/bin/pip-compile --no-emit-index-url \
      --no-emit-trusted-host \
      --resolver=backtracking \
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
      --resolver=backtracking \
      --unsafe-package=distribute \
      --unsafe-package=offby1-website \
      --unsafe-package=offby1.website \
      --unsafe-package=pip \
      --unsafe-package=setuptools \
      requirements.in

install-deps:
    .venv/bin/pip-sync requirements.txt

deps: compile-deps install-deps

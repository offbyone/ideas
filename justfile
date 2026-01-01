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

debug settings="pelicanconf.py": prepare_fonts
  uv run pelican --fatal=errors -s {{settings}} -o output content --debug

generate: (build "publishconf.py")

generate-dev: build

publish: generate upload invalidate

compile-deps:
  uv lock

update-deps:
  uv lock --upgrade

install-deps: install-python-deps install-node-deps

install-python-deps:
  uv sync

install-node-deps:
  npm install

setup-gha: install-deps
  #!/usr/bin/env bash
  # if GITHUB_PATH exists then we are in a GitHub Action, add the
  # virtual environment and node_modules to the PATH
  if [ -n "$GITHUB_PATH" ]; then
    echo "$GITHUB_WORKSPACE/.venv/bin" >> $GITHUB_PATH
    echo "$GITHUB_WORKSPACE/node_modules/.bin" >> $GITHUB_PATH
  fi

deps: compile-deps install-deps

plan:
    tofu plan -out plan.just

apply:
    tofu apply plan.just

new_post:
  uv run invoke new-post

# Verification tasks
check-code:
  uv run ruff check .
  uv run ruff format --check .

check-content:
  uv run invoke list-categories > /dev/null
  uv run invoke list-tags > /dev/null

check-links:
  uvx --from linkchecker@10.5.0 linkchecker \
      --ignore-url /tag/ \
      --no-warnings \
      output/

check-html:
  #!/usr/bin/env bash
  if [ ! -f "output/index.html" ]; then
    echo "Missing index.html"
    exit 1
  fi
  
  if ! grep -q "<html" output/index.html; then
    echo "index.html missing HTML tag"
    exit 1
  fi
  
  if ! grep -q "<title>" output/index.html; then
    echo "index.html missing title tag"
    exit 1
  fi

check-feeds:
  #!/usr/bin/env bash
  if [ -f "output/feeds/all.atom.xml" ]; then
    if ! python3 -c "import xml.etree.ElementTree as ET; ET.parse('output/feeds/all.atom.xml')"; then
      echo "RSS feed is not valid XML"
      exit 1
    fi
  fi

# Linting tasks (replaces pre-commit hooks)
lint-ruff:
  uv run ruff check .
  uv run ruff format --check .

lint-terraform:
  #!/usr/bin/env bash
  # Skip if no .tf files exist
  if ! find . -name "*.tf" -not -path "./.terraform/*" -type f | grep -q .; then
    echo "No Terraform files found, skipping terraform checks"
    exit 0
  fi
  tofu fmt -check -recursive .
  tofu validate

lint-rst:
  #!/usr/bin/env bash
  # Check for common RST mistakes (backticks without role) in .rst files only
  # Exclude plugins/ and Just-Read/ directories
  if find . -name "*.rst" -not -path "./plugins/*" -not -path "./Just-Read/*" -not -path "./.venv/*" -type f -exec grep -l -E '\`[^\`]+\`[^_]' {} \; 2>/dev/null | grep -q .; then
    echo "Found bare backticks in RST files (should use :role:\`text\` or \`\`double backticks\`\`)"
    find . -name "*.rst" -not -path "./plugins/*" -not -path "./Just-Read/*" -not -path "./.venv/*" -type f -exec grep -Hn -E '\`[^\`]+\`[^_]' {} \;
    exit 1
  fi
  echo "RST backtick check passed"

lint: lint-ruff lint-terraform lint-rst

check: check-code check-content check-links check-html check-feeds

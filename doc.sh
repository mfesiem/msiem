#!/bin/bash
# This shell script builds the manpage docs for msiem
# See the markdown file under the ./docs folder 
# and the mkdocs build under the ./site folder

set -e

# Install requirements
python3 -m pip install argparse-manpage mkdocs

git clone https://github.com/mle86/man-to-md.git || true

if ! which markdown; then
    sudo npm install markdown-to-html -g
fi

mkdir -p ./docs

# Generating documentation
MANWIDTH=120
export MANWIDTH
argparse-manpage --pyfile ./msiem/cli.py \
    --function get_parser \
    --author "Andy Walden, Tristan Landes" \
    --project-name "msiem" \
    --url https://github.com/mfesiem/msiem > msiem.1

# Delete the weird ".SS"
# List all sub commands and use the lower case name!
# Also replace the link to hithub with no name
./man-to-md/man-to-md.pl < msiem.1 | sed 's/.SS//' \
    | sed 's/Msiem Config/msiem config/' \
    | sed 's/Msiem Alarms/msiem alarms/' \
    | sed 's/Msiem Esm/msiem esm/' \
    | sed 's/Msiem Ds/msiem ds/' \
    | sed 's/Msiem Events/msiem events/' \
    | sed 's/Msiem Wl/msiem wl/' \
    | sed 's/Msiem Api/msiem api/' \
    | sed 's/The latest version of msiem may be downloaded from/The latest version of msiem may be downloaded from GitHub/' > docs/index.md

rm msiem.1

mkdocs build
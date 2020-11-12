#!/bin/bash
# This shell script builds the manpage docs for msiem. 
# I've been running it from MacOS but I beleive it's valid on Linux too. 
# See the markdown files under the ./docs folder 
# and the mkdocs build under the ./site folder

# Stop if errors
set -euo pipefail

# Install requirements
python3 -m pip install argparse-manpage mkdocs mkdocs-awesome-pages-plugin

# Cloning or pulling changes from the documentation
if [[ ! -d man-to-md ]]; then
    git clone https://github.com/mle86/man-to-md.git
else
    cd man-to-md && git pull --quiet && cd ..
fi

docsfolder="./docs/$(python3 setup.py -V)"
mkdir -p "${docsfolder}"

# Generating documentation
MANWIDTH=120
export MANWIDTH
argparse-manpage --pyfile ./msiem/cli.py \
    --function get_parser \
    --author "Andy Walden, Tristan Landes" \
    --project-name "msiem" \
    --url https://github.com/mfesiem/msiem > msiem.1

# Customize the docs with some replacements with sed
# Delete the weird ".SS"
# List all sub commands and use the lower case name!
# Replace msiem(1) by msiem <version>
# Also replace the link to github with no name
./man-to-md/man-to-md.pl < msiem.1 | sed 's/.SS//' \
    | sed 's/Msiem Config/msiem config/' \
    | sed 's/Msiem Alarms/msiem alarms/' \
    | sed 's/Msiem Esm/msiem esm/' \
    | sed 's/Msiem Ds/msiem ds/' \
    | sed 's/Msiem Events/msiem events/' \
    | sed 's/Msiem Wl/msiem wl/' \
    | sed 's/Msiem Api/msiem api/' \
    | sed 's/The latest version of msiem may be downloaded from/The latest version of msiem may be downloaded from GitHub/' \
    | sed "s/msiem(1)/msiem $(python3 setup.py -V)/" \
        > "${docsfolder}/index.md"

# Remove the raw manpage
rm msiem.1

# List all requests
echo >> "${docsfolder}/index.md"
echo "# List of all requests" >> "${docsfolder}/index.md"
echo "Generated with msiempy $(python3 -c 'from msiempy import VERSION; print(VERSION)') from ESM $(python3 -c 'from msiempy import NitroSession; print(NitroSession().version())') " >> "${docsfolder}/index.md"
echo >> "${docsfolder}/index.md"
echo "\`$ msiem api --list\`" >> "${docsfolder}/index.md"
echo >> "${docsfolder}/index.md"
echo "\`\`\`" >> "${docsfolder}/index.md"
python3 -m msiem api --list >> "${docsfolder}/index.md"
echo "\`\`\`" >> "${docsfolder}/index.md"

# Copy the docs in the versionned folder to the latest
cp "${docsfolder}/index.md" "docs/index.md"

# Build
mkdocs build
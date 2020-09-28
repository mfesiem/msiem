#!/bin/bash
set -e
python3 -m pip install argparse-manpage

# Cloning or pulling changes from the documentation
if [[ ! -d mfesiem.github.io ]]; then
    git clone https://github.com/mfesiem/mfesiem.github.io
else
    cd mfesiem.github.io && git pull --quiet && cd ..
fi

# Generating documentation
argparse-manpage --pyfile ./msiem/cli.py --function get_parser --author "Andy Walden, Tristan Landes" --project-name "msiem" > msiem.1
# echo > mfesiem.github.io/docs/msiem/index.html
# pandoc -f man -t html msiem.1 -o mfesiem.github.io/docs/msiem/index.html
# cp man.html
cat msiem.1  | groff -mandoc -Thtml > mfesiem.github.io/docs/msiem/index.html

# Pushing docs
echo "Pushing manpage"
cd mfesiem.github.io && git add . && git commit -m "Generate msiem docs $(date)" --quiet && git push origin master --quiet
cd ..

echo "Manpage at : https://mfesiem.github.io/docs/msiem/"

rm -f msiem.1
# rm -f man.html
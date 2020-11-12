# Stop if errors
set -euo pipefail

rm -rf ./dist

# Generating docs
./doc.sh

# Cloning or pulling changes from the documentation
if [[ ! -d mfesiem.github.io ]]; then
    git clone https://github.com/mfesiem/mfesiem.github.io
else
    cd mfesiem.github.io && git pull --quiet && cd ..
fi

cp -r ./site/ mfesiem.github.io/docs/msiem

# Pushing docs
echo "Pushing documentation"
cd mfesiem.github.io && git add . && git commit -m "Generate msiem docs $(date)" --quiet && git push origin master --quiet
cd ..

echo "Documentation at : https://mfesiem.github.io/docs/msiem/"

# Publishing to pypi
python3 setup.py build check sdist bdist_wheel
twine upload --verbose dist/*
python3 setup.py clean
rm -rf ./dist
rm -fr ./build
rm -fr ./msiem.egg-info

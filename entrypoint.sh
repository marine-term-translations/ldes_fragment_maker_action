#! /bin/sh
pwd

ls -al

echo "repo name is:" $GITHUB_REPOSITORY
cd ../..
pwd
ls -al
# copy over ./github/workspace/* /*
rsync --recursive --progress -avzh ./github/workspace/* ./

echo "Branch name is:" $INPUT_BRANCH

cd src
ls -al

cd ..
cd ./github/workspace
git config --global --add safe.directory /github/workspace
# set user name and email 
git config --global user.name 'GitHub Actions'
git config --global user.email 'actions@github.com'

cd ../..
cd src

python fragment_maker.py --branch $INPUT_BRANCH





# copy over everything in ./ back to ./github/workspace
# overwrite everything in ./github/workspace
# do not copy over the .git folder and the .github folder 
# also do not copy over the following files:
# - entrypoint.sh
# - Dockerfile
# - README.md
# - LICENSE
# - .gitignore
# - .dockerignore
# - .env
# package.json
# poetry.lock
# pyproject.toml
# requirements.txt
# everything in src folder and recursively under src folder
# package-lock.json
# actions.yml

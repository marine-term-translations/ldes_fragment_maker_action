#! /bin/sh
pwd

ls -al

echo "repo name is:" $GITHUB_REPOSITORY
cd ../..
pwd
ls -al


echo "Branch name is:" $INPUT_BRANCH

cd src
ls -al

cd ..
cd ./github/workspace
git config --global --add safe.directory /github/workspace
# set user name and email 
git config --global user.name 'GitHub Actions'
git config --global user.email 'actions@github.com'
git fetch --all
BRANCHES=$(git branch -a)
echo "$BRANCHES"
git pull origin $INPUT_BRANCH
git checkout main

cd ../..

# copy over ./github/workspace/* /*
rsync --recursive --progress -avzh ./github/workspace/* ./

cd src

python fragment_maker.py --branch $INPUT_BRANCH

cd ..
cd ./github/workspace
git checkout main
cd ../..
rsync --recursive --progress -avzhq \
    --exclude=.git \
    --exclude=.github \
    --exclude=.dockerenv \
    --exclude=README.md \
    --exclude=bin \
    --exclude=boot \
    --exclude=config.yml \
    --exclude=dev \
    --exclude=entrypoint.sh \
    --exclude=etc \
    --exclude=github \
    --exclude=home \
    --exclude=lib \
    --exclude=lib64 \
    --exclude=media \
    --exclude=mnt \
    --exclude=opt \
    --exclude=proc \
    --exclude=node_modules \
    --exclude=package-lock.json \
    --exclude=package.json \
    --exclude=poetry.lock \
    --exclude=pyproject.toml \
    --exclude=run \
    --exclude=root \
    --exclude=sbin \
    --exclude=src \
    --exclude=srv \
    --exclude=sys \
    --exclude=tmp \
    --exclude=usr \
    --exclude=var \
    --exclude=gathered.json \
    ./ ./github/workspace
cd ./github/workspace

# make a symlink from /LDES/latest.ttl to feed
cd ./LDES
ln -sf latest.ttl feed
cd ..
git add .
git commit -m "Adding LDES fragments for branch $INPUT_BRANCH"
git push origin main

# Check if the LDES branch exists, if not, create it
if git show-ref --quiet refs/heads/LDES; then
    echo "LDES branch exists. Checking out LDES branch."
    git checkout LDES
else
    echo "LDES branch does not exist. Creating and checking out LDES branch."
    git checkout -b LDES
fi

cd ../..
# copy over overything in the LDES folder to ./github/workspace
rsync --recursive --progress -avzhq \
    --exclude=.git \
    --exclude=.github \
    --exclude=.dockerenv \
    --exclude=README.md \
    --exclude=bin \
    --exclude=boot \
    --exclude=config.yml \
    --exclude=dev \
    --exclude=entrypoint.sh \
    --exclude=etc \
    --exclude=github \
    --exclude=home \
    --exclude=lib \
    --exclude=lib64 \
    --exclude=media \
    --exclude=mnt \
    --exclude=opt \
    --exclude=proc \
    --exclude=node_modules \
    --exclude=package-lock.json \
    --exclude=package.json \
    --exclude=poetry.lock \
    --exclude=pyproject.toml \
    --exclude=run \
    --exclude=root \
    --exclude=sbin \
    --exclude=src \
    --exclude=srv \
    --exclude=sys \
    --exclude=tmp \
    --exclude=usr \
    --exclude=var \
    --exclude=gathered.json \
    ./LDES ./github/workspace

cd ./github/workspace
git add .
git commit -m "Adding LDES fragments for branch $INPUT_BRANCH"
git push origin LDES

# Now we can copy over the LDES folder into the gh-pages branch
git checkout gh-pages
cd ../..
rsync --recursive --progress -avzhq \
    --exclude=.git \
    --exclude=.github \
    --exclude=.dockerenv \
    --exclude=README.md \
    --exclude=bin \
    --exclude=boot \
    --exclude=config.yml \
    --exclude=dev \
    --exclude=entrypoint.sh \
    --exclude=etc \
    --exclude=github \
    --exclude=home \
    --exclude=lib \
    --exclude=lib64 \
    --exclude=media \
    --exclude=mnt \
    --exclude=opt \
    --exclude=proc \
    --exclude=node_modules \
    --exclude=package-lock.json \
    --exclude=package.json \
    --exclude=poetry.lock \
    --exclude=pyproject.toml \
    --exclude=run \
    --exclude=root \
    --exclude=sbin \
    --exclude=src \
    --exclude=srv \
    --exclude=sys \
    --exclude=tmp \
    --exclude=usr \
    --exclude=var \
    --exclude=gathered.json \
    ./LDES ./github/workspace

cd ./github/workspace
# symlink feed to latest
cd ./LDES
ln -sf latest.ttl feed
cd ..
git add .
git commit -m "Adding LDES fragments made from processing data in branch $INPUT_BRANCH"
git push origin gh-pages
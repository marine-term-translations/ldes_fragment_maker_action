# use a python image
FROM python:3.11

# install node and npm
RUN apt-get update
RUN apt-get install -y nodejs npm

# install rsync
RUN apt-get install -y rsync

# copy over src folder
COPY src /src

# install dependencies
RUN pip install poetry
RUN pip install pyyaml pycountry validators pyrdfj2 rdflib
RUN pip install git+https://github.com/vliz-be-opsci/py-sema.git

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

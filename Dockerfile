FROM debian:bookworm-slim

# Install core libs
RUN apt-get update  \
    && apt-get upgrade -y  \
    && apt-get install -y  \
    apt-utils  \
    netcat-traditional  \
    binutils  \
    libproj-dev  \
    libpq-dev  \
    gdal-bin

# Install dependencies
RUN apt-get install -y  \
    build-essential  \
    libssl-dev  \
    zlib1g-dev  \
    libbz2-dev  \
    libreadline-dev  \
    libsqlite3-dev  \
    wget  \
    curl  \
    llvm  \
    libncurses5-dev  \
    libncursesw5-dev  \
    xz-utils  \
    tk-dev  \
    libffi-dev  \
    liblzma-dev  \
    python3-openssl  \
    git

## User preparation
#RUN useradd --create-home app
#WORKDIR /home/app
#RUN mkdir -p /home/app/libs
#WORKDIR /home/app/libs
#ENV PYTHONPATH="/home/app/libs"


# Install pyenv
RUN mkdir -p /home/app/libs
ENV PYENV_ROOT="/usr/local/pyenv"
RUN git clone https://github.com/pyenv/pyenv.git $PYENV_ROOT

## Set pyenv environment variables
#ENV PATH="$PYENV_ROOT/bin:$PATH"
#
## Install all versions of Python greater than 3.8
#RUN pyenv update  \
#    && pyenv install 3.8  \
#    && pyenv install 3.9  \
#    && pyenv install 3.10  \
#    && pyenv install 3.11  \
#    && pyenv install 3.12  \
#    && pyenv global 3.8 3.9 3.10 3.11 3.12
#
## Clean up
#RUN apt-get clean && \
#    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
#
## Install poetry
#RUN pip3.8 install -U pip poetry
#
## Copy source code and setup environment
#COPY . /home/app/libs
#RUN chown -R app:app /home/app/libs
#USER app
#RUN poetry install
#RUN pre-commit install
#RUN pre-commit run -a
#RUN tox

FROM python:3.7-alpine

ENV PYCURL_SSL_LIBRARY=openssl \
    PYTHONPATH=. \
    PATH="/root/.poetry/bin:$PATH" \
    DOCKER=True

# compile requirements for some python libraries
RUN apk --no-cache add curl-dev bash postgresql-dev \
    build-base libffi-dev libressl-dev tini curl

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python3 && \
    export PYCURL_SSL_LIBRARY=openssl && \
    poetry config settings.virtualenvs.create false

WORKDIR /app
# install python reqs
COPY ["pyproject.toml", "poetry.lock", "/app/"]

RUN poetry install -vvv --no-dev

# build frontend
COPY dmeister/static /app/dmeister/static
RUN apk --no-cache add nodejs npm git && \
    npm install -g yarn && \
    cd /app/dmeister/static && \
    yarn && \
    yarn build && \
    apk --no-cache del nodejs git && \
    rm -rf node_modules spec src bin &&  \
    cd /app


EXPOSE 8080
COPY . /app
CMD ["tini", "./startup.sh"]

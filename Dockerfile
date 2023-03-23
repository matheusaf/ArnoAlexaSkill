ARG version=3.9.16-alpine3.16
FROM python:${version} AS base
WORKDIR /app
RUN adduser -S -D -H pypy
COPY ./poetry.lock .
COPY ./pyproject.toml .
RUN ["python", "-m", "pip", "install", "poetry"]
RUN ["poetry", "config", "virtualenvs.in-project", "true"]
RUN ["poetry", "install"]

USER pypy:1001
COPY --chown=pypy:pypy ./src ./src
CMD ["sleep", "infinity"]

FROM base AS producer
CMD ["python", "src/main.py"]

FROM base AS consumer
WORKDIR /app/src
CMD ["poetry", "run", "python", "main.py"]

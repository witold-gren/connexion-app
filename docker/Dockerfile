# choosing the lightest python image
FROM jfloff/alpine-python:3.7-slim as base

# set specific environment variables for python
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 VIRTUAL_ENV=/opt/venv

FROM base as builder

# create one virtual environment for install all library in one place
RUN python3 -m venv $VIRTUAL_ENV

# add this folder to environment path
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy important dependencies
COPY ./backend/requirements.txt /requirements.txt

# Install app dependencies
RUN apk update \
    && apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev \
    && pip install -r /requirements.txt

FROM base

# add new folder to environment path
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# create folder and set default path
WORKDIR /app

# copy only build library from first build stage
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

# copy another important files and app
COPY ./backend ./docker/entrypoint.sh ./docker/start.sh ./docker/gunicorn.sh /app/

# Add libpq for psycopg2 library, create user, move file to root
RUN apk --no-cache add libpq \
    && addgroup -S flask \
    && adduser -h /home/flask -S -G flask flask \
    && chown -R flask /app \
    && mv /app/entrypoint.sh /app/start.sh /app/gunicorn.sh / \
    && chmod +x /entrypoint.sh /start.sh /gunicorn.sh

# set default user as flask
USER flask

# expose defalt flask port
EXPOSE 5000

# set entrypoint and default command
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/start.sh"]

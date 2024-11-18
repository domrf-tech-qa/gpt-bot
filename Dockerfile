# first stage
FROM python:3.8 AS builder
COPY requirements.txt .
# install dependencies to the local user directory (eg. /root/.local)
RUN pip install --user -r requirements.txt
RUN apt-get update && apt-get install libpq5 -y
# second stage
FROM python:3.8-slim
WORKDIR /code
# copy only the dependencies that are needed for our application and the source files
COPY --from=builder /root/.local /root/.local
COPY ./src .
# update PATH
ENV PATH=/root/.local:$PATH
RUN chmod 644 /usr/local/share/ca-certificates/foo.crt && update-ca-certificates

# make sure you include the -u flag to have our stdout logged
CMD [ "python", "-u", "./main.py" ]
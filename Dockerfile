###########
# BUILDER #
###########

# pull official base image
FROM python:3.11-slim-buster as builder

# set work directory 
WORKDIR /usr/src/app

# set environment variables 
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY ./requirements.txt .
# Ensure that Gunicorn and any other required packages are included in your requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

#########
# FINAL #
#########

# pull official base image
FROM python:3.11-slim-buster

# Installing netcat, which is used in the entrypoint.sh to wait for the Postgres server
# Also including 'build-essential' for compiling Python packages with native extensions
RUN apt-get update && apt-get install -y --no-install-recommends netcat build-essential && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies from wheels built in the builder stage
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# set work directory
WORKDIR /usr/src/app

#test

# Copy the rest of your application code
COPY ./ ./

# Ensure entrypoint.sh has Unix line endings
RUN sed -i 's/\r$//' /usr/src/app/entrypoint.sh

# Ensure entrypoint.sh is executable
RUN chmod +x /usr/src/app/entrypoint.sh

# Update the entrypoint to use the entrypoint.sh script
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

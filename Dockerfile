# Use the official Alpine Linux base image
FROM alpine:latest

# Install necessary packages for all languages
RUN apk add --no-cache \
    build-base \
    g++ \
    gcc \
    openjdk17 \
    python3 \
    nodejs \
    npm \
    && rm -rf /var/cache/apk/*

# Install TypeScript for JavaScript (if needed)
RUN npm install -g typescript

# Create a non-root user for safety
RUN adduser -D dockeruser

# Set up the work directory
WORKDIR /app

# Set the default user to non-root user
USER dockeruser

# CMD to keep the container running in an interactive shell
CMD ["/bin/sh"]

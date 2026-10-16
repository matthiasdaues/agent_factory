# Render image for publish-docs: Quarkdown, Chromium, Python and poppler.
#
# What: Holds the tools that turn a Quarkdown build into a checked PDF.
#       The factory files (_docs_assemble.py, pipeline.sh, render.js,
#       publish.css) are mounted at run time, so editing them needs no rebuild.
# When: Built by `publish-docs pdf` on first use, tagged with a hash of
#       this file.
# By:   packages/factory/scripts/publish-docs.

FROM mcr.microsoft.com/playwright:v1.54.1-noble

ARG QUARKDOWN_VERSION=2.6.4
ARG QUARKDOWN_SHA256=b2ec84dbae47925a2db92aa3bc085ee8aec03fec69b82629d8619164bfd75b02

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3-yaml poppler-utils unzip curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL -o /tmp/quarkdown.zip \
      "https://github.com/iamgio/quarkdown/releases/download/v${QUARKDOWN_VERSION}/quarkdown-linux-x64.zip" \
 && echo "${QUARKDOWN_SHA256}  /tmp/quarkdown.zip" | sha256sum -c - \
 && unzip -q /tmp/quarkdown.zip -d /opt \
 && rm /tmp/quarkdown.zip

WORKDIR /opt/publish-docs
RUN npm init -y >/dev/null && npm install --omit=dev --no-audit --no-fund playwright-core@1.54.1

# The Quarkdown start script finds its bundled Java runtime relative to its
# own path, so it goes on PATH instead of behind a symlink.
ENV PATH=/opt/quarkdown/bin:$PATH \
    NODE_PATH=/opt/publish-docs/node_modules \
    HOME=/tmp

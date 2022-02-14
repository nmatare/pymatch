# DESCRIPTION: pymatch dockerfile

ARG IMAGE=python:3.7.11
ARG IMAGE_TAG=-slim-buster

FROM ${IMAGE}${IMAGE_TAG}
LABEL maintainer "Nathan Matare <nathan.matare@gmail.com>"

ARG EXTENSIONS=[tests]
ARG GID=1000
ARG UID=1000

# Add non-root user `pymatch`
RUN addgroup --gid ${GID} pymatch \
  && adduser --disabled-password --gecos '' --shell /bin/bash \
    --uid ${UID} --gid ${GID} pymatch

SHELL ["/bin/bash", "-c"]

USER root

# See http://bugs.python.org/issue19846
ENV \
  DEBIAN_FRONTEND=noninteractive \
  LANG=C.UTF-8 \
  LC_ALL=C.UTF-8

# Install package
WORKDIR /tmp

COPY . .

RUN pip install -e ".${EXTENSIONS}" \
  && mv tools/docker/entrypoint.sh /usr/bin \
  && chmod +x /usr/bin/entrypoint.sh \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /var/cache/*/* /var/log/* \
  && rm -rf /var/cache/oracle-jdk11-installer \
  && chown -R pymatch:pymatch /tmp /home/pymatch \
  && apt-get autoremove

WORKDIR /home/pymatch

USER pymatch

ENTRYPOINT ["/usr/bin/entrypoint.sh"]

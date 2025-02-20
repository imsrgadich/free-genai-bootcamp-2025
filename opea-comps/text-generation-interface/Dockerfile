# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

FROM python:3.11-slim

RUN apt-get update -y && apt-get install -y --no-install-recommends --fix-missing \
    libgl1-mesa-glx \
    libjemalloc-dev

RUN useradd -m -s /bin/bash user && \
    mkdir -p /home/user && \
    chown -R user /home/user/

COPY text-generation-interface /home/user/text-generation-interface

RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r /home/user/text-generation-interface/requirements.yml

ENV PYTHONPATH=$PYTHONPATH:/home/user

USER user

WORKDIR /home/user/text-generation-interface

ENTRYPOINT ["bash", "entrypoint.sh"]
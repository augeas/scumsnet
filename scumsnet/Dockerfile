FROM python:3.6-alpine

ENV RUNTIME_PACKAGES libxslt libxml2 git curl libpq
ENV BUILD_PACKAGES build-base libxslt-dev libxml2-dev libffi-dev python3-dev openssl-dev

COPY requirements.txt /

RUN apk add --no-cache ${RUNTIME_PACKAGES} ${BUILD_PACKAGES} \
	&& pip install -r requirements.txt \
	&& apk del ${BUILD_PACKAGES} \
	&& rm -rf /root/.cache

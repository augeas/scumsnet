FROM python:3.6-alpine

ENV RUNTIME_PACKAGES libstdc++ libxslt libxml2 git curl libpq runit bash
ENV BUILD_PACKAGES build-base libxslt-dev libxml2-dev libffi-dev python3-dev jpeg-dev zlib-dev openssl-dev

COPY requirements.txt /

RUN apk add --no-cache ${RUNTIME_PACKAGES} ${BUILD_PACKAGES} \
	&& pip install -r requirements.txt \
	&& python3 -m spacy download en_core_web_sm \
	&& apk del ${BUILD_PACKAGES} \
	&& rm -rf /root/.cache 


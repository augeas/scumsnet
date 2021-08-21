FROM python:3.6-alpine

ENV RUNTIME_PACKAGES libstdc++ libxslt libxml2 git curl libpq runit bash libzmq 
ENV BUILD_PACKAGES build-base libxslt-dev libxml2-dev libffi-dev python3-dev jpeg-dev zlib-dev openssl-dev rust cargo zeromq-dev

COPY requirements.txt /

RUN apk add --no-cache ${RUNTIME_PACKAGES} ${BUILD_PACKAGES} \
    && python3 -m pip install --upgrade pip \
    && pip install cryptography pyzmq \
	&& pip install -r requirements.txt \
	&& python3 -m spacy download en_core_web_sm \
	&& apk del ${BUILD_PACKAGES} \
	&& rm -rf /root/.cache 

RUN pip install git+https://github.com/iamumairayub/scrapyd-client.git --upgrade
		
COPY scrapy.cfg /
RUN mkdir scumsnet && mkdir -p /etc/service && mkdir -p /root/logs
ADD ./scumsnet /scumsnet
ADD ./service /etc/service

CMD ["runsvdir", "/etc/service"]



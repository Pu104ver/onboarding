FROM  cr.yandex/mirror/library/node:18 as builder

WORKDIR /usr/src/app
ARG FQDN=onboarding.billed.pro
ADD *.json ./
ADD *.config.ts ./

RUN npm install

COPY . .

ENV REACT_APP_BASE_URL=https://$FQDN/api/
ENV REACT_APP_API_BASE_URL=https://$FQDN/api/

RUN npm run build

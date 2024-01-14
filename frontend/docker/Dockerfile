FROM node:20.10.0-bullseye-slim as base

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
ENV NODE_ENV="production"

FROM base as deps

WORKDIR /app

ADD package.json yarn.lock ./
RUN yarn install --frozen-lockfile --network-timeout 100000

FROM base as production-deps

WORKDIR /app

ADD package.json yarn.lock ./
RUN yarn install --frozen-lockfile --production --network-timeout 100000

FROM base as build

WORKDIR /app

COPY --from=deps /app/node_modules /app/node_modules

ADD . .
RUN yarn build

FROM base as production

WORKDIR /app

COPY --from=production-deps /app/node_modules /app/node_modules

COPY --from=build /app/dist /app/dist
COPY --from=build /app/public /app/public
COPY --from=build /app/package.json /app/package.json

CMD ["yarn", "preview"]
FROM node:24-alpine AS dependencies

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./

RUN npm ci


FROM node:24-alpine AS builder

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=dependencies /app/node_modules ./node_modules
COPY frontend/ ./

RUN npm run build


FROM node:24-alpine AS runtime

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    HOSTNAME=0.0.0.0 \
    PORT=3000

WORKDIR /app

RUN addgroup \
        --system \
        --gid 10001 \
        appgroup \
    && adduser \
        --system \
        --uid 10001 \
        --ingroup appgroup \
        appuser

COPY --from=builder \
    --chown=appuser:appgroup \
    /app/public \
    ./public

COPY --from=builder \
    --chown=appuser:appgroup \
    /app/.next/standalone \
    ./

COPY --from=builder \
    --chown=appuser:appgroup \
    /app/.next/static \
    ./.next/static

USER 10001:10001

EXPOSE 3000

CMD ["node", "server.js"]
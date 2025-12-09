FROM node:20-alpine AS deps
LABEL maintainer="News Chat Team"
LABEL description="React News Chat Application - Dependencies Stage"

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci --omit=dev --ignore-scripts && \
    npm cache clean --force

FROM node:20-alpine AS builder
LABEL description="React News Chat Application - Build Stage"

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY package.json package-lock.json ./

RUN npm ci --ignore-scripts

COPY . .

ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV NODE_ENV=production
RUN npm run build

FROM nginx:1.25-alpine AS production
LABEL maintainer="News Chat Team"
LABEL description="React News Chat Application - Production"

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

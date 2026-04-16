FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_AUTH_API_URL=http://localhost:8001
ARG VITE_SPATIAL_API_URL=http://localhost:8000
ARG VITE_MIND_MAPPER_API_URL=http://localhost:8002
ARG VITE_NOTIFICATIONS_API_URL=http://localhost:8005
ARG VITE_REALTIME_WS_URL=ws://localhost:8004
ENV VITE_AUTH_API_URL=$VITE_AUTH_API_URL
ENV VITE_SPATIAL_API_URL=$VITE_SPATIAL_API_URL
ENV VITE_MIND_MAPPER_API_URL=$VITE_MIND_MAPPER_API_URL
ENV VITE_NOTIFICATIONS_API_URL=$VITE_NOTIFICATIONS_API_URL
ENV VITE_REALTIME_WS_URL=$VITE_REALTIME_WS_URL
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

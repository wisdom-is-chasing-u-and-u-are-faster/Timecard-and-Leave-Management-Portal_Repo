# Multi-Stage Build for GCP Cloud Run
# Base Image: Node.js 20 LTS Alpine
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests
COPY package*.json tsconfig*.json ./

# Install all dependencies including devDependencies for build
RUN npm ci

# Copy source and public static assets
COPY src/ ./src/
COPY public/ ./public/
COPY db/ ./db/

# Build TypeScript to dist
RUN npm run build

# Production Runner Image
FROM node:20-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production
ENV PORT=8080

# Install production dependencies only
COPY package*.json ./
RUN npm ci --only=production

# Copy compiled files and assets from builder
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/public ./public
COPY --from=builder /app/db ./db

# Cloud Run listens on PORT env
EXPOSE 8080

CMD ["node", "dist/main.js"]

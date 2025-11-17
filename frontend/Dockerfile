# ============================================================================
# RAIA Frontend - Production Dockerfile (Multi-stage build)
# ============================================================================

# Stage 1: Build the application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create non-root user
RUN addgroup -g 1000 raia && \
    adduser -D -u 1000 -G raia raia && \
    chown -R raia:raia /usr/share/nginx/html && \
    chown -R raia:raia /var/cache/nginx && \
    chown -R raia:raia /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R raia:raia /var/run/nginx.pid

USER raia

# Expose port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5173/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

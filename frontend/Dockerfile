# Multi-stage Dockerfile for Kairos BCP Frontend
# Optimized for production deployment with Next.js 15

# Dependencies stage
FROM node:20-alpine as deps

# Set working directory
WORKDIR /app

# Add non-root user for security
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --only=production --omit=dev && npm cache clean --force

# Builder stage
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install all dependencies (including devDependencies)
RUN npm ci

# Copy source code
COPY . .

# Set environment variables for build
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine as production

WORKDIR /app

# Set environment variables
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Add non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy runtime dependencies from deps stage
COPY --from=deps --chown=nextjs:nodejs /app/node_modules ./node_modules

# Copy built application from builder stage
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Create uploads directory for user content
RUN mkdir -p /app/uploads && chown nextjs:nodejs /app/uploads

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Set environment variable for hostname
ENV HOSTNAME="0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Start the application
CMD ["node", "server.js"]

# Development stage
FROM node:20-alpine as development

WORKDIR /app

# Install development dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Add non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy source code
COPY --chown=nextjs:nodejs . .

# Ensure .next directory exists and is writable by the nextjs user
RUN mkdir -p /app/.next && chown -R nextjs:nodejs /app/.next

# Create uploads directory and ensure it's writable
RUN mkdir -p /app/uploads && chown -R nextjs:nodejs /app/uploads

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Set environment variables for development
ENV NODE_ENV development
ENV NEXT_TELEMETRY_DISABLED 1

# Start development server with hot reload
CMD ["npm", "run", "dev"]

# Testing stage
FROM builder as testing

# Install testing dependencies
RUN npm ci

# Copy test configuration
COPY . .

# Run tests
RUN npm run lint
RUN npm run build

# Create test reports directory
RUN mkdir -p /app/test-reports

# Run any additional tests if available
# RUN npm run test:ci
# RUN npm run test:e2e

# Build optimization stage
FROM node:20-alpine as optimizer

WORKDIR /app

# Install bundle analyzer
RUN npm install -g @next/bundle-analyzer

# Copy built application
COPY --from=builder /app .

# Analyze bundle size
RUN npx @next/bundle-analyzer

# Security scanning stage
FROM production as security

# Switch to root for security tools
USER root

# Install security scanning tools
RUN apk add --no-cache npm audit-ci

# Copy package files for security scan
COPY package.json package-lock.json* ./

# Run security audit
RUN npm audit --audit-level=moderate || true

# Run additional security checks if tools are available
# RUN npm audit --json > /app/security-report.json || true

# Switch back to nextjs user
USER nextjs
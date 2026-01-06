# Build stage
FROM rust:1.83-slim-bookworm AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*

# Copy manifests
COPY Cargo.toml Cargo.lock* ./

# Create dummy source to cache dependencies
RUN mkdir src && echo "fn main() {}" > src/main.rs && echo "" > src/lib.rs
RUN cargo build --release
RUN rm -rf src

# Copy actual source
COPY src ./src

# Build for release
RUN touch src/main.rs src/lib.rs && cargo build --release

# Runtime stage
FROM debian:bookworm-slim

WORKDIR /app

# Install runtime dependencies (including PostgreSQL client for import check)
RUN apt-get update && apt-get install -y ca-certificates libssl3 postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy binaries from builder
COPY --from=builder /app/target/release/dixi-backend /app/dixi-backend
COPY --from=builder /app/target/release/import /app/import

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV HOST=0.0.0.0
ENV PORT=8080
ENV RUST_LOG=info

EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]

# cpp-frame: two-stage build. Stage 1 downloads header-only deps, compiles main.cpp.

FROM debian:bookworm-slim AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

# Pinned upstream versions (reproducible curl fetches during docker build).
ARG CPP_HTTPLIB_VERSION=v0.18.3
ARG NLJSON_VERSION=v3.11.3

RUN mkdir -p third_party \
    && curl -fsSL -o third_party/httplib.h \
        "https://raw.githubusercontent.com/yhirose/cpp-httplib/${CPP_HTTPLIB_VERSION}/httplib.h" \
    && curl -fsSL -o third_party/json.hpp \
        "https://github.com/nlohmann/json/releases/download/${NLJSON_VERSION}/json.hpp"

COPY main.cpp .

RUN g++ -std=c++17 -Wall -Wextra -Werror -pthread -I. -o cpp-frame main.cpp

FROM debian:bookworm-slim

WORKDIR /app
COPY --from=builder /src/cpp-frame /app/cpp-frame

EXPOSE 8002

CMD ["/app/cpp-frame"]

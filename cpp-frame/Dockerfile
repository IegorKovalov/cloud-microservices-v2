# cpp-frame — Phase 6: two-stage build. Stage 1 compiles; stage 2 runs only the binary.

FROM debian:bookworm-slim AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY hello.cpp .
RUN g++ -std=c++17 -Wall -Wextra -Werror -o hello hello.cpp

FROM debian:bookworm-slim

WORKDIR /app
COPY --from=builder /src/hello /app/hello

CMD ["/app/hello"]

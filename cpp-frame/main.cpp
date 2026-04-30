// cpp-frame: C++ HTTP edge for frame processing. Phase 7: GET /health only.

#include "third_party/httplib.h"

#include "third_party/json.hpp"

int main() {
  httplib::Server server;

  server.Get("/health", [](const httplib::Request& /*request*/,
                            httplib::Response& response) {
    const nlohmann::json body = {{"status", "ok"}};
    response.set_content(body.dump(), "application/json");
  });

  if (!server.listen("0.0.0.0", 8002)) {
    return 1;
  }
  return 0;
}

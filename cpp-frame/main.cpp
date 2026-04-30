// cpp-frame: C++ HTTP edge for frame processing. Phase 8: GET /health,
// POST /process_frame (pixels + threshold → bright_pixel_count) via 2 threads + mutex.

#include <mutex>
#include <thread>
#include <vector>

#include "third_party/httplib.h"

#include "third_party/json.hpp"

int main() {
  httplib::Server server;

  server.Get("/health", [](const httplib::Request& /*request*/,
                            httplib::Response& response) {
    const nlohmann::json body = {{"status", "ok"}};
    response.set_content(body.dump(), "application/json");
  });

  server.Post("/process_frame",
              [](const httplib::Request& request, httplib::Response& response) {
                try {
                  const auto j = nlohmann::json::parse(request.body);
                  const std::vector<double> pixels =
                      j.at("pixels").get<std::vector<double>>();
                  const double threshold = j.at("threshold").get<double>();

                  const size_t n = pixels.size();
                  const size_t mid = n / 2;
                  std::mutex mtx;
                  unsigned long long bright_pixel_count = 0;

                  auto worker = [&](size_t start, size_t end) {
                    unsigned long long local = 0;
                    for (size_t i = start; i < end; ++i) {
                      if (pixels[i] >= threshold) {
                        ++local;
                      }
                    }
                    std::lock_guard<std::mutex> lock(mtx);
                    bright_pixel_count += local;
                  };

                  std::thread t1(worker, 0, mid);
                  std::thread t2(worker, mid, n);
                  t1.join();
                  t2.join();

                  const nlohmann::json body = {
                      {"bright_pixel_count", bright_pixel_count}};
                  response.set_content(body.dump(), "application/json");
                } catch (const nlohmann::json::exception& e) {
                  response.status = 400;
                  const nlohmann::json err = {{"error", e.what()}};
                  response.set_content(err.dump(), "application/json");
                }
              });

  if (!server.listen("0.0.0.0", 8002)) {
    return 1;
  }
  return 0;
}

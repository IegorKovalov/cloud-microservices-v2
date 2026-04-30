// cpp-frame: C++ HTTP edge for frame processing. GET /health, GET /metrics,
// POST /process_frame (pixels + threshold → bright_pixel_count) via 2 threads
// + mutex; global metrics protected by a separate mutex.

#include <mutex>
#include <thread>
#include <vector>

#include "third_party/httplib.h"

#include "third_party/json.hpp"

namespace {

std::mutex g_metrics_mutex;
unsigned long long g_request_count = 0;
unsigned long long g_error_count = 0;

void IncRequest() {
  std::lock_guard<std::mutex> lock(g_metrics_mutex);
  ++g_request_count;
}

void IncError() {
  std::lock_guard<std::mutex> lock(g_metrics_mutex);
  ++g_error_count;
}

nlohmann::json MetricsBody() {
  std::lock_guard<std::mutex> lock(g_metrics_mutex);
  return nlohmann::json{{"request_count", g_request_count},
                        {"error_count", g_error_count}};
}

}  // namespace

int main() {
  httplib::Server server;

  server.Get("/health", [](const httplib::Request& /*request*/,
                            httplib::Response& response) {
    IncRequest();
    const nlohmann::json body = {{"status", "ok"}};
    response.set_content(body.dump(), "application/json");
  });

  server.Get("/metrics", [](const httplib::Request& /*request*/,
                            httplib::Response& response) {
    IncRequest();
    const nlohmann::json body = MetricsBody();
    response.set_content(body.dump(), "application/json");
  });

  server.Post("/process_frame",
              [](const httplib::Request& request, httplib::Response& response) {
                IncRequest();
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
                  IncError();
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

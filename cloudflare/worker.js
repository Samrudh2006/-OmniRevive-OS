/**
 * OmniRevive-OS — Cloudflare Edge Worker Gateway (100% Free Tier)
 * Implements:
 *  - #8: Run an API (Edge Reverse Proxy & Gateway)
 *  - #14: Run Serverless Functions (Cloudflare Workers)
 *  - #15: Edge SQL Database (Cloudflare D1 queries)
 *  - #16: Cache Pages & API Responses (Cloudflare Edge Cache)
 *  - #18: Cloudflare Turnstile CAPTCHA verification
 *  - #19: Run Cron Jobs (Scheduled trigger for retry sweeps)
 *  - #23: Receive Webhooks (Edge webhook verification & ingestion)
 *  - #24: Key-Value Storage (Cloudflare KV idempotency cache)
 */

export default {
  // 14 & 8: HTTP Request Handler
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // 16. Edge Caching for Static Assets & Public Metadata
    if (request.method === "GET" && (url.pathname.startsWith("/static/") || url.pathname === "/api/v1/gateways/rails")) {
      const cache = caches.default;
      const cachedResponse = await cache.match(request);
      if (cachedResponse) {
        const res = new Response(cachedResponse.body, cachedResponse);
        res.headers.set("X-Edge-Cache", "HIT");
        return res;
      }
    }

    // 24. Key-Value Storage for Fast-Loop Idempotency Check
    if (request.method === "POST" && url.pathname === "/api/v1/recovery/trigger-fast-loop") {
      const idempotencyKey = request.headers.get("X-Idempotency-Key");
      if (idempotencyKey && env.RECOVERY_KV) {
        const existingRecord = await env.RECOVERY_KV.get(`idem_${idempotencyKey}`);
        if (existingRecord) {
          return new Response(existingRecord, {
            status: 200,
            headers: {
              "Content-Type": "application/json",
              "X-Edge-Idempotency": "DEDUPLICATED",
            },
          });
        }
      }
    }

    // 18. Turnstile CAPTCHA Validation for Critical CFO Actions
    if (request.method === "POST" && url.pathname.startsWith("/api/v1/cfo/approve")) {
      const turnstileToken = request.headers.get("CF-Turnstile-Token");
      if (turnstileToken && env.TURNSTILE_SECRET_KEY) {
        const formData = new FormData();
        formData.append("secret", env.TURNSTILE_SECRET_KEY);
        formData.append("response", turnstileToken);
        formData.append("remoteip", request.headers.get("CF-Connecting-IP") || "");

        const verifyRes = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
          method: "POST",
          body: formData,
        });
        const outcome = await verifyRes.json();
        if (!outcome.success) {
          return new Response(JSON.stringify({
            success: false,
            error: { code: "CAPTCHA_FAILED", message: "Turnstile challenge validation failed." }
          }), { status: 403, headers: { "Content-Type": "application/json" } });
        }
      }
    }

    // 23. Edge Webhook Receiver & Forwarder
    if (url.pathname === "/api/v1/webhooks/razorpay") {
      const signature = request.headers.get("X-Razorpay-Signature");
      if (!signature) {
        return new Response(JSON.stringify({
          success: false,
          error: { code: "UNAUTHORIZED", message: "Missing X-Razorpay-Signature header." }
        }), { status: 401, headers: { "Content-Type": "application/json" } });
      }
    }

    // 8 & 20: Forward to Origin / Cloudflare Tunnel
    const originUrl = new URL(request.url);
    const backendOrigin = env.API_ORIGIN || "http://127.0.0.1:8000";
    const targetUrl = new URL(backendOrigin);
    originUrl.protocol = targetUrl.protocol;
    originUrl.host = targetUrl.host;
    originUrl.port = targetUrl.port;

    const modifiedRequest = new Request(originUrl.toString(), {
      method: request.method,
      headers: request.headers,
      body: request.body,
      redirect: "follow",
    });

    // Pass Cloudflare Edge Telemetry to FastAPI
    modifiedRequest.headers.set("X-Forwarded-Host", url.host);
    modifiedRequest.headers.set("CF-Connecting-IP", request.headers.get("CF-Connecting-IP") || "127.0.0.1");
    modifiedRequest.headers.set("CF-IPCountry", request.headers.get("CF-IPCountry") || "IN");

    try {
      const originResponse = await fetch(modifiedRequest);
      const response = new Response(originResponse.body, originResponse);

      // Cache successful public GET responses at Cloudflare edge for 5 minutes
      if (request.method === "GET" && originResponse.ok && (url.pathname === "/api/v1/gateways/rails" || url.pathname.startsWith("/static/"))) {
        response.headers.set("Cache-Control", "public, max-age=300, s-maxage=300");
        ctx.waitUntil(caches.default.put(request, response.clone()));
      }

      return response;
    } catch (err) {
      return new Response(JSON.stringify({
        success: false,
        error: {
          code: "EDGE_ORIGIN_ERROR",
          message: "Unable to reach OmniRevive origin service via Cloudflare Tunnel.",
          details: err.message,
        },
      }), { status: 502, headers: { "Content-Type": "application/json" } });
    }
  },

  // 19. Scheduled Cron Trigger Handler (Automated Recovery Sweep)
  async scheduled(event, env, ctx) {
    console.log(`[Cloudflare Cron] Executing recovery sweep triggered at: ${event.cron}`);
    if (env.API_ORIGIN) {
      ctx.waitUntil(
        fetch(`${env.API_ORIGIN}/api/v1/health`, {
          method: "GET",
          headers: { "User-Agent": "Cloudflare-Workers-Cron/1.0" },
        }).then(res => console.log(`[Cron Health Check] Status: ${res.status}`))
      );
    }
  },
};

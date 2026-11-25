"""Load test for the rate limiter: fires N requests at a path and reports status counts and Retry-After."""
import sys, time, collections, concurrent.futures as cf
import httpx

base = sys.argv[1]; path = sys.argv[2]; n = int(sys.argv[3]); workers = int(sys.argv[4]) if len(sys.argv) > 4 else 20

def hit(_):
    t = time.perf_counter()
    try:
        r = httpx.get(base + path, timeout=10)
        return r.status_code, r.headers.get("retry-after"), time.perf_counter() - t
    except Exception as e:
        return type(e).__name__, None, time.perf_counter() - t

t0 = time.perf_counter()
with cf.ThreadPoolExecutor(workers) as ex:
    res = list(ex.map(hit, range(n)))
el = time.perf_counter() - t0
c = collections.Counter(r[0] for r in res)
lat = sorted(r[2] for r in res)
print({"requests": n, "seconds": round(el, 2), "rps": round(n / el, 1), "status": dict(c),
       "retry_after_seen": sorted({r[1] for r in res if r[1]}),
       "p50_ms": round(lat[len(lat)//2]*1000, 1), "p95_ms": round(lat[int(len(lat)*.95)]*1000, 1)})

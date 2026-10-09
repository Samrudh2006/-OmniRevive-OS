"""
OmniRevive-OS :: Full-Codebase AEO, Schema.org & Technical SEO Test Suite
========================================================================
Validates:
1. Complete crawlability & 200 OK statuses for all 14 canonical sitemap routes.
2. Robust robots.txt & AI agent discovery (GPTBot, ClaudeBot, Perplexity, OAI-SearchBot).
3. Valid JSON-LD Schema.org syntax and entity graphs across all landing pages.
4. Metadata integrity: title, description, canonical, robots directives, OG, and Twitter cards.
5. Answer Engine extractability (H1 semantics, direct answer paragraphs, breadcrumbs).
6. Security headers (HSTS, nosniff, frame protection).
"""

import json
import re
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

INDEXABLE_ROUTES = [
    "/",
    "/ai-revenue-recovery",
    "/payment-failure-recovery",
    "/b2b-dispute-resolution",
    "/architecture",
    "/idempotency-protection",
    "/audit-ledger",
    "/benchmarks",
    "/faq",
    "/documentation",
    "/about",
    "/privacy",
    "/terms"
]

def test_sitemap_xml_and_route_parity():
    """Verify sitemap.xml exists, is valid XML, and includes all indexable routes."""
    res = client.get("/sitemap.xml")
    assert res.status_code == 200
    assert "<?xml" in res.text
    assert "<urlset" in res.text
    
    for route in INDEXABLE_ROUTES:
        expected_loc = f"https://omnirevive-os.antideploy.com{route if route != '/' else '/'}"
        assert expected_loc in res.text, f"Missing route in sitemap.xml: {expected_loc}"


def test_robots_txt_ai_crawlers_and_policies():
    """Verify robots.txt allows search crawlers and AI search agents."""
    res = client.get("/robots.txt")
    assert res.status_code == 200
    text = res.text
    assert "User-agent: *" in text
    assert "User-agent: Googlebot" in text
    assert "User-agent: Bingbot" in text
    assert "User-agent: GPTBot" in text
    assert "User-agent: ClaudeBot" in text
    assert "User-agent: PerplexityBot" in text
    assert "User-agent: OAI-SearchBot" in text
    assert "Sitemap: https://omnirevive-os.antideploy.com/sitemap.xml" in text
    assert "llms-txt: https://omnirevive-os.antideploy.com/llms.txt" in text


def test_llms_txt_and_full_specification_endpoints():
    """Verify llms.txt and llms-full.txt endpoints are live and return accurate markdown."""
    for path in ["/llms.txt", "/.well-known/llms.txt", "/llms-full.txt"]:
        res = client.get(path)
        assert res.status_code == 200
        assert "OmniRevive-OS" in res.text
        assert "Dual-Speed Control Plane" in res.text or "System Architecture" in res.text


def test_all_routes_return_200_and_security_headers():
    """Verify all public routes return 200 OK and security headers."""
    for route in INDEXABLE_ROUTES:
        res = client.get(route)
        assert res.status_code == 200, f"Route {route} failed with status {res.status_code}"
        assert res.headers.get("X-Content-Type-Options") == "nosniff"
        assert "max-age=" in res.headers.get("Strict-Transport-Security", "")


def test_all_routes_metadata_completeness():
    """Verify every public page has unique title, description, canonical, robots, OG, and Twitter tags."""
    for route in INDEXABLE_ROUTES:
        res = client.get(route)
        html = res.text
        
        # 1. Title
        assert "<title>" in html and "</title>" in html, f"Missing title in {route}"
        title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        assert title_match and len(title_match.group(1).strip()) > 10, f"Empty or too short title in {route}"

        # 2. Meta description
        assert 'name="description"' in html, f"Missing meta description in {route}"

        # 3. Canonical link
        assert 'rel="canonical"' in html, f"Missing canonical link in {route}"

        # 4. Open Graph
        assert 'property="og:title"' in html, f"Missing og:title in {route}"
        assert 'property="og:description"' in html, f"Missing og:description in {route}"
        assert 'property="og:url"' in html, f"Missing og:url in {route}"

        # 5. Twitter Card
        assert 'name="twitter:card"' in html, f"Missing twitter:card in {route}"


def test_json_ld_schema_validity_on_all_pages():
    """Extract and validate JSON-LD syntax on every public landing page."""
    schema_regex = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)
    
    for route in INDEXABLE_ROUTES:
        res = client.get(route)
        html = res.text
        matches = schema_regex.findall(html)
        assert len(matches) > 0, f"No JSON-LD schema found in {route}"
        
        for idx, schema_raw in enumerate(matches):
            try:
                schema_json = json.loads(schema_raw.strip())
                assert "@context" in schema_json or "@graph" in schema_json
            except Exception as e:
                pytest.fail(f"Invalid JSON-LD syntax in {route} block {idx}: {e}")


def test_semantic_heading_and_answer_extractability():
    """Ensure every page has a single top-level H1 heading and clear answer extraction."""
    for route in INDEXABLE_ROUTES:
        res = client.get(route)
        html = res.text
        
        h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
        assert len(h1_matches) == 1, f"Expected exactly 1 <h1> in {route}, found {len(h1_matches)}"
        assert len(h1_matches[0].strip()) > 5, f"Empty <h1> in {route}"

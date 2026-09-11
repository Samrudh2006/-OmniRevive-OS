import os
import pytest
from backend.app import __version__
from backend.app.config import settings

def test_version_and_metadata():
    assert __version__ == "1.0.0"

def test_default_boundary_settings():
    assert settings.ENABLE_TRAI_COMPLIANCE is True
    assert settings.MAX_RETRY_ATTEMPTS == 3
    assert settings.MAX_DISCOUNT_PERCENT == 10.0
    assert settings.MAX_DISCOUNT_AMOUNT_INR == 500.0
    assert settings.HIGH_VALUE_THRESHOLD_INR == 50000.0
    assert settings.MIN_CONFIDENCE_THRESHOLD == 0.60
    assert settings.HIGH_VALUE_CONFIDENCE_THRESHOLD == 0.85

def test_architecture_documentation_exists():
    arch_path = os.path.join(os.path.dirname(__file__), "..", "ARCHITECTURE.md")
    assert os.path.exists(arch_path)
    with open(arch_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Three-Tier Financial Isolation Boundary Pattern" in content
        assert "HMAC SHA-256" in content
        assert "Poisson" in content

def test_seo_crawler_endpoints():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    client = TestClient(app)
    
    # Test robots.txt
    res_robots = client.get("/robots.txt")
    assert res_robots.status_code == 200
    assert "User-agent: *" in res_robots.text
    assert "Sitemap:" in res_robots.text

    # Test sitemap.xml
    res_sitemap = client.get("/sitemap.xml")
    assert res_sitemap.status_code == 200
    assert "<?xml" in res_sitemap.text
    assert "<urlset" in res_sitemap.text
    assert "<loc>" in res_sitemap.text

    # Test HTML SEO meta tags
    res_html = client.get("/")
    assert res_html.status_code == 200
    assert '<meta name="description"' in res_html.text
    assert '<meta property="og:title"' in res_html.text
    assert '<meta name="twitter:card"' in res_html.text
    assert 'application/ld+json' in res_html.text
    assert '<h1' in res_html.text


import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_frontend_root_serves_modular_html(client):
    res = client.get("/")
    assert res.status_code == 200
    text = res.text
    assert "/static/main.js" in text
    assert "/static/styles/main.css" in text
    assert "cfo_approvals" in text
    assert "cfo-queue-tbody" in text
    assert "view-cfo_approvals" in text
    # Ensure massive monolithic inline script blocks were unbundled
    assert "function mountComponents() {" not in text
    assert "<script type=\"module\" src=\"/static/main.js\"></script>" in text

def test_frontend_static_assets_served(client):
    # Main JS
    res_js = client.get("/static/main.js")
    assert res_js.status_code == 200
    assert "window.switchNavTab" in res_js.text
    assert "window.runBenchmarkAction" in res_js.text
    assert "refreshCfoQueueUI" in res_js.text

    # Main CSS
    res_css = client.get("/static/styles/main.css")
    assert res_css.status_code == 200
    assert len(res_css.text) > 5000

    # Modular Services
    for svc in ["apiClient.js", "recoveryService.js", "b2bVoiceService.js", "cfoService.js", "auditService.js"]:
        res_svc = client.get(f"/static/services/{svc}")
        assert res_svc.status_code == 200, f"Failed to fetch /static/services/{svc}"
        assert len(res_svc.text) > 100

    # Modular Utils
    for util in ["formatters.js", "toast.js", "audioPlayer.js"]:
        res_util = client.get(f"/static/utils/{util}")
        assert res_util.status_code == 200, f"Failed to fetch /static/utils/{util}"
        assert len(res_util.text) > 100

    # Modular Components
    for comp in ["topologyCanvas.js", "weibullChart.js", "cfoApprovalModal.js", "copilotDrawer.js", "cedarModal.js"]:
        res_comp = client.get(f"/static/components/{comp}")
        assert res_comp.status_code == 200, f"Failed to fetch /static/components/{comp}"
        assert len(res_comp.text) > 100

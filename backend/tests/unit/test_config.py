from backend.app.core.config import settings

def test_settings_loaded():
    assert settings.APP_NAME == "Autonomous Video AI Platform"
    assert settings.MOCK_EXTERNAL_APIS is True
    assert settings.DEFAULT_WORKSPACE_BUDGET_USD > 0
    assert settings.API_V1_PREFIX == "/api/v1"

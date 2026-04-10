"""
Set test credentials in the environment before any app module is imported.
conftest.py is loaded by pytest before test modules, so Settings() will
be initialised with these values when app.config is first imported.
"""
import os

os.environ.setdefault("LIVEKIT_URL", "wss://test.livekit.cloud")
os.environ.setdefault("LIVEKIT_API_KEY", "test-api-key")
os.environ.setdefault("LIVEKIT_API_SECRET", "test-api-secret-that-is-long-enough")

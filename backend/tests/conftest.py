"""Test environment.

Settings are populated with placeholders before anything imports the app, so
the suite runs without a .env and never touches a real project. Environment
variables take precedence over the .env file, so a developer with real
credentials on disk still gets an isolated run.

Nothing here should ever hold a working credential: no test may reach a live
service.
"""

import os

os.environ.setdefault("GEMINI_API_KEY", "test-key-not-real")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-key-not-real")

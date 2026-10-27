"""Dedicated manual-only entry point. No mail or local AI services are imported."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("app.py")),
               init_globals={"PUBLIC_DEMO_ENTRY": True}, run_name="__main__")

from embed_bridge import render_embed_bridge
render_embed_bridge()

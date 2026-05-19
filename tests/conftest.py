"""Pytest config + shared fixtures for aspire_dash."""
import os
import sys

# Make package importable from the repo root without `pip install -e .`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def is_dash_component(obj) -> bool:
    """True if `obj` looks like a Dash component (has .to_plotly_json or .children)."""
    return hasattr(obj, "to_plotly_json") or hasattr(obj, "children")

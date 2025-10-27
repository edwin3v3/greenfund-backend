"""Small recommendation helper used by multiple routers.

This module provides a lightweight async function `generate_recommendations`
that returns an empty list for now. It intentionally avoids importing
heavy dependencies so it can be imported by `app.routers.climate`.
"""

from typing import Any, Dict, List, Optional


async def generate_recommendations(
    weather_data: Dict[str, Any],
    activities: List[Any],
    current_crop: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return a list of recommendation dicts based on inputs.

    This is a minimal placeholder implementation to satisfy imports and
    avoid runtime ImportError. Replace with real logic when ready.
    """
    # keep implementation minimal and dependency-free
    return []

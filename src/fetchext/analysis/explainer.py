from typing import Dict, Optional
from fetchext.analysis.permissions_db import PERMISSIONS_DB


def explain_permission(permission: str) -> Optional[Dict[str, str]]:
    """
    Returns the description and risk level for a given permission.

    Args:
        permission: The permission string (e.g., "tabs", "storage").

    Returns:
        A dictionary with "description" and "risk" keys, or None if not found.
    """
    # Direct match
    if permission in PERMISSIONS_DB:
        return PERMISSIONS_DB[permission]

    # Host permission check (simple heuristic)
    if "://" in permission or permission == "<all_urls>":
        return {
            "description": f"Grants access to data on {permission}.",
            "risk": "High" if permission == "<all_urls>" else "Medium",
        }

    return None


def get_all_permissions() -> Dict[str, Dict[str, str]]:
    """Returns the entire permissions database."""
    return PERMISSIONS_DB

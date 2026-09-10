"""
MillenniumIT ESP Brand Assets & Logo Components
Provides consistent corporate branding across all pages, tabs, sidebars, and exports.
"""

import os
import base64
from PIL import Image

BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

FAVICON_PATH = os.path.join(ASSETS_DIR, "favicon.png")
LOGO_FULL_PATH = os.path.join(ASSETS_DIR, "logo_full.png")
LOGO_H_PATH = os.path.join(ASSETS_DIR, "logo_horizontal.png")
LOGO_MARK_PATH = os.path.join(ASSETS_DIR, "logo_mark.png")


def get_favicon():
    """Returns a PIL Image of the official MillenniumIT ESP red logo mark for st.set_page_config."""
    if os.path.exists(FAVICON_PATH):
        try:
            return Image.open(FAVICON_PATH)
        except Exception:
            pass
    return "🚘"


def get_logo_b64(which="horizontal"):
    """Returns base64 encoded string of requested logo asset."""
    path_map = {
        "horizontal": LOGO_H_PATH,
        "full": LOGO_FULL_PATH,
        "mark": LOGO_MARK_PATH,
        "favicon": FAVICON_PATH
    }
    target = path_map.get(which, LOGO_H_PATH)
    if os.path.exists(target):
        try:
            with open(target, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            pass
    return ""


def render_brand_header(badge_text="AI MOBILITY DISPATCH", height_px=36):
    """Renders sleek top hero header with the official corporate horizontal logo without any Markdown indentation."""
    b64 = get_logo_b64("horizontal")
    if b64:
        badge_html = f'<span style="background: rgba(66, 138, 255, 0.15); border: 1px solid rgba(66, 138, 255, 0.35); color: #82B1FF; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 6px; letter-spacing: 0.8px;">{badge_text}</span>' if badge_text else ''
        return f'<div style="display: inline-flex; align-items: center; gap: 14px; margin-bottom: 8px; flex-wrap: wrap;"><img src="data:image/png;base64,{b64}" style="height: {height_px}px; width: auto; object-fit: contain; filter: drop-shadow(0 4px 14px rgba(239, 65, 35, 0.25));" alt="MillenniumIT ESP">{badge_html}</div>'
    return ''


def render_sidebar_logo():
    """Renders the official stacked MillenniumIT ESP logo for the sidebar without any Markdown indentation."""
    b64 = get_logo_b64("full")
    if b64:
        return f'<div style="text-align: center; padding: 14px 12px; margin-bottom: 14px; background: linear-gradient(180deg, rgba(239, 65, 35, 0.10) 0%, rgba(16, 22, 34, 0.5) 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);"><img src="data:image/png;base64,{b64}" style="max-width: 175px; height: auto; object-fit: contain; filter: drop-shadow(0 4px 12px rgba(239, 65, 35, 0.35));" alt="MillenniumIT ESP"><div style="color: #94A3B8; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-top: 6px;">Corporate Mobility Fleet</div></div>'
    return ''

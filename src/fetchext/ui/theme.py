from textual.app import App
from fetchext.config import load_config
import logging

logger = logging.getLogger(__name__)

DEFAULT_THEME = {
    "primary": "#00ff00",
    "secondary": "#ff00ff",
    "background": "#111111",
    "surface": "#222222",
    "error": "#ff0000",
    "warning": "#ffa500",
    "success": "#00ff00",
    "info": "#0000ff"
}

def apply_theme(app: App):
    """
    Apply theme from config to the Textual app.
    """
    try:
        config = load_config()
        theme_config = config.get("tui", {}).get("theme", {})
        
        # Merge with default
        theme = DEFAULT_THEME.copy()
        theme.update(theme_config)
        
        # Generate CSS variables
        css_vars = []
        for key, value in theme.items():
            # Textual uses specific variable names for some things, but we can define our own
            # or override standard ones if we knew them.
            # For now, let's define custom ones and use them in our CSS.
            css_vars.append(f"$theme-{key}: {value};")
            
            # Map to standard Textual variables where possible
            if key == "primary":
                css_vars.append(f"$primary: {value};")
            elif key == "secondary":
                css_vars.append(f"$secondary: {value};")
            elif key == "background":
                css_vars.append(f"$background: {value};")
            elif key == "surface":
                css_vars.append(f"$surface: {value};")
            elif key == "error":
                css_vars.append(f"$error: {value};")
        
        # Inject into app
        # Textual doesn't have a direct "inject CSS variables" method easily exposed 
        # without subclassing or using design system.
        # However, we can append to the app's CSS.
        
        # We define variables at the top level (global scope)
        css_block = "\n".join([f"{line}" for line in css_vars])
        
        # This is a bit hacky, but Textual apps concatenate CSS.
        # We need to make sure this loads BEFORE other CSS or has higher specificity?
        # Actually, variables are resolved at usage.
        
        # Let's try to modify the App's CSS class attribute if possible, or just return the CSS
        # and have the app include it.
        
        return css_block
        
    except Exception as e:
        logger.error(f"Failed to load theme: {e}")
        return ""

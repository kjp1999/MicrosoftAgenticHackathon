from typing import List, Dict
from pywinauto import Desktop
from playwright.sync_api import sync_playwright


def get_windows_buttons() -> List[Dict]:
    """
    Get UI buttons from visible Windows applications.

    Returns:
        List of button metadata from desktop apps.
    """
    desktop = Desktop(backend="uia")
    buttons = []

    for window in desktop.windows():
        try:
            for el in window.descendants():
                info = el.element_info
                if info.control_type == "Button":
                    buttons.append({
                        "text": info.name,
                        "automation_id": info.automation_id,
                        "control_type": info.control_type,
                        "rectangle": {
                            "left": info.rectangle.left,
                            "top": info.rectangle.top,
                            "right": info.rectangle.right,
                            "bottom": info.rectangle.bottom
                        },
                        "app": window.window_text(),
                        "process_id": info.process_id
                    })
        except:
            continue

    return buttons
def get_browser_buttons(profile_path: str, chrome_path: str) -> list:
    buttons = []
    try:
        with sync_playwright() as p:
            # Launch without closing the browser when the context closes
            browser = p.chromium.launch_persistent_context(
                user_data_dir=profile_path,
                headless=False,
                executable_path=chrome_path,
                args=['--start-maximized', '--disable-extensions']
            )
            
            # Check if there are existing pages, otherwise create one
            page = browser.pages[0] if len(browser.pages) > 0 else browser.new_page()
            
            # Wait longer for the page to stabilize
            page.wait_for_load_state("networkidle", timeout=30000)
            
            # Navigate only if needed (if not already on a page)
            current_url = page.url
            if current_url == "about:blank" or not current_url.startswith("http"):
                page.goto("https://www.google.com", timeout=30000)
                page.wait_for_load_state("networkidle", timeout=30000)
            
            # Collect all interactive elements (not just buttons)
            for selector in ["button", "input[type='button']", "a", ".button", "[role='button']"]:
                elements = page.query_selector_all(selector)
                for element in elements:
                    try:
                        bbox = element.bounding_box()
                        if bbox:  # Only include visible elements
                            text = element.inner_text() or element.get_attribute("value") or element.get_attribute("aria-label") or ""
                            buttons.append({
                                "text": text,
                                "rectangle": {
                                    "left": int(bbox["x"]),
                                    "top": int(bbox["y"]),
                                    "right": int(bbox["x"] + bbox["width"]),
                                    "bottom": int(bbox["y"] + bbox["height"])
                                }
                            })
                    except Exception as e:
                        continue
                        
            # Don't close the browser automatically
            # browser.close() - intentionally leaving the browser open
    except Exception as e:
        print(f"Error in get_browser_buttons: {e}")
    return buttons
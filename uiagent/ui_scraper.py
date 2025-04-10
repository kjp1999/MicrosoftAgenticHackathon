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


def get_browser_buttons(profile_path: str, chrome_path: str) -> List[Dict]:
    """
    Scrape DOM buttons from a Chrome tab using Playwright.

    Args:
        profile_path: Chrome user profile path.
        chrome_path: Path to Chrome executable.

    Returns:
        List of button/anchor metadata.
    """
    buttons = []
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            executable_path=chrome_path,
            headless=False
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        page.wait_for_timeout(1500)
        elements = page.locator("button, a")

        for i in range(elements.count()):
            el = elements.nth(i)
            try:
                text = el.inner_text().strip()
                box = el.bounding_box()
                if text and box:
                    buttons.append({
                        "text": text,
                        "bounding_box": box
                    })
            except:
                continue

        browser.close()

    return buttons

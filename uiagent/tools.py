import time
import pyautogui
import json
from PIL import ImageGrab
import ollama
from ui_scraper import get_windows_buttons, get_browser_buttons

LLM_MODEL = "llama3.1"
VISION_MODEL = "llava"

def perform_mouse_action(x, y, action="left click"):
    try:
        # Move to position with a smoother motion
        pyautogui.moveTo(x, y, duration=0.5)
        
        # Wait a bit before clicking
        time.sleep(0.5)
        
        if action == "left click":
            pyautogui.click()
        elif action == "right click":
            pyautogui.rightClick()
        elif action == "double click":
            pyautogui.doubleClick()
            
        # Wait after clicking
        time.sleep(1)
        return f"✅ Successfully performed {action} at coordinates ({x}, {y})"
    except Exception as e:
        return f"❌ Mouse action failed: {str(e)}"

def take_screenshot(path="screen.png") -> str:
    ImageGrab.grab().save(path)
    return path

def analyze_image_with_llava(image_path: str, instruction: str) -> dict:
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    response = ollama.chat(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
            "content": f"Where should I click to '{instruction}'? Return JSON with x, y, and label.",
            "images": [image_bytes]
        }]
    )
    try:
        return json.loads(response["message"]["content"])
    except:
        return {"x": 0, "y": 0, "text": "parse error"}

def match_coordinates(vision_target: dict, ui_buttons: list, tolerance=40) -> dict:
    vx, vy = vision_target.get("x"), vision_target.get("y")
    for btn in ui_buttons:
        rect = btn.get("rectangle")
        if not rect:
            continue
        bx = (rect["left"] + rect["right"]) // 2
        by = (rect["top"] + rect["bottom"]) // 2
        if abs(vx - bx) <= tolerance and abs(vy - by) <= tolerance:
            return {"x": bx, "y": by, "text": btn["text"]}
    return {}

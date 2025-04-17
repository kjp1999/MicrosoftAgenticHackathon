from langgraph.graph import StateGraph
from tools import *
import pyautogui
import time

# === LangGraph Node Functions ===

def receive_instruction(state: dict) -> dict:
    state.update({
        "instruction": state["input"],
        "retries": 0,
        "done": False
    })
    return state

def scrape_ui(state: dict) -> dict:
    buttons = []
    try:
        buttons += get_windows_buttons()
    except Exception as e:
        print(f"⚠️ get_windows_buttons failed: {e}")
    try:
        buttons += get_browser_buttons(
            profile_path=r"C:\\Users\\kjp19\\Downloads\\chrome_temp_profile",
            chrome_path=r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        )
    except Exception as e:
        print(f"⚠️ get_browser_buttons failed: {e}")
    state.update({"buttons": buttons})
    return state

def screenshot(state: dict) -> dict:
    path = take_screenshot()
    state.update({"screenshot": path})
    return state

def vision_inference(state: dict) -> dict:
    result = analyze_image_with_llava(
        state["screenshot"],
        state["instruction"]
    )
    state.update({"vision_target": result})
    return state

def match_ui(state: dict) -> dict:
    match = match_coordinates(state["vision_target"], state["buttons"])
    state.update({"match": match})
    return state

def act_on_match(state: dict) -> dict:
    match = state.get("match")
    if match:
        try:
            # Add a small delay before mouse movement to improve reliability
            time.sleep(0.5)
            
            # Get screen dimensions
            screen_width, screen_height = pyautogui.size()
            
            # Safety check - make sure coordinates are not too close to screen edges
            safe_x = max(10, min(match["x"], screen_width - 10))
            safe_y = max(10, min(match["y"], screen_height - 10))
            
            # Use safe coordinates to avoid the fail-safe areas
            result = perform_mouse_action(safe_x, safe_y, "left click")
            
            # Check if the result contains an error message
            if "❌" in result:
                state["retries"] += 1
                state.update({
                    "result": f"{result}. Retry #{state['retries']}",
                    "done": False,
                    "last_action": f"click {safe_x},{safe_y}"
                })
                print(f"Action failed, retrying ({state['retries']}/10)...")
            else:
                state.update({
                    "result": result, 
                    "done": False,  # Not done until verified
                    "last_action": f"click {safe_x},{safe_y}"
                })
                print("Action executed, verifying success...")
        except Exception as e:
            state["retries"] += 1
            state.update({
                "result": f"❌ Mouse action failed: {str(e)}. Retry #{state['retries']}",
                "done": False,
                "last_action": f"attempted click {safe_x},{safe_y}"
            })
            print(f"Exception occurred, retrying ({state['retries']}/10): {str(e)}")
    else:
        state["retries"] += 1
        state.update({
            "result": f"⚠️ No matching UI element found. Retry #{state['retries']}",
            "done": False,
            "last_action": "search for UI element"
        })
        print(f"No match found, retrying ({state['retries']}/10)...")
    return state

def verify_completion(state: dict) -> dict:
    """Verify that the instruction has been successfully completed"""
    # Take a new screenshot to analyze the current state
    verification_screenshot = take_screenshot()
    
    # Analyze the screenshot to see if the command has been fulfilled
    verification_prompt = f"""Verify if this action was successful: "{state['instruction']}".
    The last action performed was: {state.get('last_action', 'unknown')}.
    Has the requested action been completed successfully? Look for visual evidence."""
    
    verification_result = analyze_image_with_llava(
        verification_screenshot,
        verification_prompt
    )
    
    # Check for success indicators in the verification result
    success_indicators = ["successful", "completed", "success", "done", "accomplished"]
    failure_indicators = ["failed", "not completed", "error", "unsuccessful", "couldn't find"]
    
    # Analyze the verification result
    success_score = sum(1 for indicator in success_indicators if indicator.lower() in verification_result.lower())
    failure_score = sum(1 for indicator in failure_indicators if indicator.lower() in verification_result.lower())
    
    if success_score > failure_score:
        state.update({
            "verification_result": "✅ Verification confirms success: " + verification_result[:100],
            "done": True
        })
        print("✅ Verification successful!")
    else:
        state.update({
            "verification_result": "❌ Verification indicates failure: " + verification_result[:100],
            "done": False
        })
        state["retries"] += 1
        print(f"❌ Verification failed, retrying ({state['retries']}/10)...")
    
    return state

def respond(state: dict) -> dict:
    if state.get("done"):
        msg = f"✅ Successfully completed: {state['instruction']}\n{state.get('verification_result', '')}"
    elif state.get("retries", 0) >= 10:
        msg = f"❌ Max retries (10) reached. Giving up on: {state['instruction']}\nLast result: {state.get('result', '')}"
    else:
        msg = state.get("result", "Done.")
    state.update({"output": msg})
    return state

# === Retry Decision Logic ===

def check_retry(state: dict) -> str:
    if state.get("done") == True:
        print("✅ Success detected - proceeding to response")
        return "success"
    elif state.get("retries", 0) >= 10:
        print("❌ Max retries reached - giving up")
        return "fail"
    else:
        print(f"🔄 Retry #{state['retries']} - starting new attempt")
        # Add a delay between retries
        time.sleep(1)
        return "retry"

# === Build LangGraph ===

builder = StateGraph(dict)

builder.add_node("receive_instruction", receive_instruction)
builder.add_node("scrape_ui", scrape_ui)
builder.add_node("screenshot", screenshot)
builder.add_node("vision_inference", vision_inference)
builder.add_node("match_ui", match_ui)
builder.add_node("act_on_match", act_on_match)
builder.add_node("verify_completion", verify_completion)
builder.add_node("respond", respond)

builder.set_entry_point("receive_instruction")

# Main linear flow
builder.add_edge("receive_instruction", "scrape_ui")
builder.add_edge("scrape_ui", "screenshot")
builder.add_edge("screenshot", "vision_inference")
builder.add_edge("vision_inference", "match_ui")
builder.add_edge("match_ui", "act_on_match")
builder.add_edge("act_on_match", "verify_completion")

# Retry / exit control flow
builder.add_conditional_edges(
    "verify_completion",
    check_retry,
    {
        "success": "respond",
        "fail": "respond",
        "retry": "screenshot"
    }
)

# Final graph
graph = builder.compile()
graph = graph.with_config({"recall": True})  # Preserve all keys
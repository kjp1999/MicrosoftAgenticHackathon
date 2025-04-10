# main.py

import subprocess
import tempfile
import ollama
from ui_scraper import get_windows_buttons, get_browser_buttons


def write_and_run_python(code: str) -> str:
    """
    Write and run Python code.

    Args:
        code: Raw Python source code to execute.

    Returns:
        str: Output or error from the code.
    """
    try:
        preamble = (
            "import os\n"
            "import subprocess\n"
            "import time\n"
            "from playwright.sync_api import sync_playwright\n"
            "\n"
            "def launch_browser():\n"
            "    with sync_playwright() as p:\n"
            "        browser = p.chromium.launch(headless=False)\n"
            "        page = browser.new_page()\n"
            "        return page, browser\n"
            "page, browser = launch_browser()\n"
        )

        full_code = preamble + "\n" + code
        print("💻 Code to execute:\n" + full_code)

        # Optional syntax check
        try:
            compile(full_code, '<temp>', 'exec')
        except SyntaxError as e:
            return f"❌ Syntax error: {e}"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(full_code)
            path = f.name

        result = subprocess.run(["python", path], capture_output=True, text=True, timeout=30)

        if result.stderr:
            return f"⚠️ Error:\n{result.stderr.strip()}"
        return f"✅ Output:\n{result.stdout.strip() or '(no output)'}"

    except Exception as e:
        return f"❌ Exception: {e}"


# === Tools available to the model ===
available_tools = {
    "get_windows_buttons": get_windows_buttons,
    "get_browser_buttons": lambda: get_browser_buttons(
        profile_path=r"C:\Users\kjp19\Downloads\chrome_temp_profile",
        chrome_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    ),
    "write_and_run_python": write_and_run_python,
}


def chat_loop():
    print("🤖 Ollama agent with tool calling is ready. Type 'exit' to quit.\n")

    messages = [{
        "role": "system",
        "content": (
            "You are a local Python agent with access to real tools.\n"
            "- Use `get_windows_buttons()` to scrape UI from Windows apps.\n"
            "- Use `get_browser_buttons()` to scrape DOM buttons from a browser.\n"
            "- Use `write_and_run_python(code: str)` to run Python code.\n"
            "- If the user wants to automate a browser search, use the `page` object from Playwright.\n"
            "- `page` and `browser` are already initialized. You can call methods like:\n"
            "  page.goto('https://www.google.com')\n"
            "  page.locator('input[name=\"q\"]').fill('sandals')\n"
            "  page.keyboard.press('Enter')"
        )
    }]

    while True:
        user_input = input("\n> ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break

        messages.append({"role": "user", "content": user_input})

        response = ollama.chat(
            model="llama3.1",  # Replace with a tool-compatible model
            messages=messages,
            tools=list(available_tools.values())
        )

        message = response["message"]
        tool_calls = message.get("tool_calls", [])

        if tool_calls:
            for call in tool_calls:
                fn_name = call["function"]["name"]
                args = call["function"].get("arguments", {})

                print(f"\n🛠 Calling tool: {fn_name}({args})")
                tool_fn = available_tools.get(fn_name)

                if not tool_fn:
                    print(f"❌ Function '{fn_name}' not found.")
                    continue

                try:
                    result = tool_fn(**args)
                    if not isinstance(result, str):
                        result = str(result)
                except Exception as e:
                    result = f"❌ Error running tool: {e}"

                print(f"\n🔧 Tool Output:\n{result}")
                messages.append({
                    "role": "tool",
                    "name": fn_name,
                    "content": result
                })

                followup = ollama.chat(
                    model="llama3.1",
                    messages=messages,
                    tools=list(available_tools.values())
                )
                follow_msg = followup["message"]
                print(f"\n🤖 {follow_msg['content']}")
                messages.append({"role": "assistant", "content": follow_msg["content"]})

        else:
            print(f"\n🤖 {message['content']}")
            messages.append({"role": "assistant", "content": message["content"]})


if __name__ == "__main__":
    chat_loop()

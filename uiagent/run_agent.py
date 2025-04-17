from agent_graph import graph
import time

def run_agent(user_input):
    print("🧠 Running multimodal UI agent...")
    start_time = time.time()
    
    try:
        result = graph.invoke({"input": user_input})
        print(f"⏱️ Completed in {time.time() - start_time:.2f} seconds")
        print(f"🔄 Retries: {result.get('retries', 0)}")
        print(f"✅ Final Output: {result.get('output', '')}")
        return result
    except Exception as e:
        print(f"❌ Agent failed: {str(e)}")
        return {"output": f"Error: {str(e)}"}

if __name__ == "__main__":
    while True:
        try:
            user_input = input("\n> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                break
                
            run_agent(user_input)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
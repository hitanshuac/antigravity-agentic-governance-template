import sys
import json
import os
from datetime import datetime, timezone

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("{}")
        return

    # PostToolUse payload has 'error' if tool failed
    error_msg = input_data.get("error")
    if not error_msg:
        print("{}")
        return
        
    tool_call = input_data.get("toolCall", {})
    tool_name = tool_call.get("name", "unknown_tool")

    log_path = os.path.join("data", "error_logs.json")
    os.makedirs("data", exist_ok=True)
    
    logs = []
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
                if not isinstance(logs, list):
                    logs = []
        except Exception:
            logs = []
            
    new_log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error_type": "ToolExecutionError",
        "component": tool_name,
        "message": error_msg[:500],
        "status": "UNRESOLVED",
        "resolution_strategy": None
    }
    
    logs.append(new_log)
    
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        import logging
        logging.error(f"Failed to write to error_logs.json: {e}")
        
    print("{}")

if __name__ == "__main__":
    import logging
    import traceback
    
    os.makedirs("data", exist_ok=True)
    logging.basicConfig(filename="data/hook_telemetry.log", level=logging.ERROR, 
                        format="%(asctime)s - error_hook - %(levelname)s - %(message)s")
    
    try:
        main()
    except Exception as e:
        logging.error(f"Failed to execute error_hook: {e}\n{traceback.format_exc()}")
        print("{}")

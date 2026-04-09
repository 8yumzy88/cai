import os
import sys
import requests
import importlib.util

# --- Configuration ---
# The exact model tag you specified
REQUIRED_MODEL = "Lily-Cybersecurity-7B-v0_2_Q4_K_M"
OLLAMA_URL = "http://localhost:11434"

# ANSI Colors for readability
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check_step(name, status, message=""):
    if status:
        print(f"[{GREEN}PASS{RESET}] {name}")
    else:
        print(f"[{RED}FAIL{RESET}] {name}: {message}")
        return False
    return True

def validate_environment():
    print(f"--- Starting Validation on {sys.platform} ---\n")
    all_pass = True

    # 1. Check OpenAI Key
    api_key = os.getenv("OPENAI_API_KEY")
    if check_step("OpenAI API Key Environment Variable", api_key is not None, "OPENAI_API_KEY is missing from environment"):
        # masked print
        print(f"       Key found: {api_key[:8]}...")
    else:
        all_pass = False

    # 2. Check CAI Framework Installation
    # Checking for common package names. Adjust if your specific fork uses a different name.
    cai_spec = importlib.util.find_spec("cai_framework") or importlib.util.find_spec("cai")
    if check_step("CAI Framework Installed", cai_spec is not None, "Could not import 'cai_framework' or 'cai'. Check 'pip list'."):
        print(f"       Location: {cai_spec.origin}")
    else:
        all_pass = False

    # 3. Check Ollama Connectivity
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if check_step("Ollama Service Running", response.status_code == 200, "Could not connect to localhost:11434"):
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            # 4. Check for Specific Custom Model
            # Ollama usually appends ':latest' if not specified, so we check loosely
            found_model = any(REQUIRED_MODEL in name for name in model_names)
            
            if check_step(f"Model '{REQUIRED_MODEL}' Loaded", found_model, f"Available models: {model_names}"):
                print(f"       Model validated ready for inference.")
            else:
                print(f"       {YELLOW}ACTION REQUIRED:{RESET} Run 'ollama pull' or create the Modelfile for {REQUIRED_MODEL}")
                all_pass = False
    except requests.exceptions.ConnectionError:
        check_step("Ollama Service Running", False, "Connection refused. Is Ollama.app running?")
        all_pass = False

    # 5. Check Jan (File System Check only)
    jan_path = "/Applications/Jan.app"
    if check_step("Jan Application Found", os.path.exists(jan_path), "Jan.app not found in /Applications"):
        print("       Jan is installed.")

    print("\n--- Validation Complete ---")
    if all_pass:
        print(f"{GREEN}SUCCESS: System is ready for hybrid AI operations.{RESET}")
    else:
        print(f"{RED}FAILURE: Please fix the errors above before running scripts.{RESET}")

if __name__ == "__main__":
    validate_environment()

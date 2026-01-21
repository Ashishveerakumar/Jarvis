"""
Script to download/pull LLaMA model via Ollama
"""
import subprocess
import sys


def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def pull_model(model_name: str = "llama2"):
    """
    Pull/download a model via Ollama
    
    Args:
        model_name: Name of the model to download
    """
    print("=" * 60)
    print("LLaMA Model Downloader (via Ollama)")
    print("=" * 60)
    print()
    
    if not check_ollama_installed():
        print("❌ Ollama is not installed!")
        print()
        print("Please install Ollama first:")
        print("  1. Download from: https://ollama.ai/download")
        print("  2. Install and run Ollama")
        print("  3. Run this script again")
        return False
    
    print(f"✅ Ollama is installed")
    print(f"📦 Pulling model: {model_name}")
    print()
    print("This may take a while depending on your internet connection...")
    print()
    
    # Pull the model
    result = subprocess.run(
        ["ollama", "pull", model_name],
        capture_output=False
    )
    
    if result.returncode == 0:
        print()
        print("=" * 60)
        print(f"✅ Model '{model_name}' downloaded successfully!")
        print()
        print("Update your .env file with:")
        print(f"OLLAMA_MODEL={model_name}")
        print()
        print("Available LLaMA models:")
        print("  - llama2 (7B parameters, ~4GB)")
        print("  - llama2:13b (13B parameters, ~8GB)")
        print("  - llama2:70b (70B parameters, ~40GB)")
        print("  - codellama (Code-specialized)")
        print("  - mistral (Fast alternative)")
        print("=" * 60)
        return True
    else:
        print(f"❌ Failed to download model: {model_name}")
        return False


def list_models():
    """List available local models"""
    result = subprocess.run(
        ["ollama", "list"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("Available local models:")
        print(result.stdout)
    else:
        print("Could not list models")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download LLaMA model via Ollama")
    parser.add_argument(
        "--model",
        default="llama2",
        help="Model name to download (e.g., llama2, llama2:13b, mistral)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available local models"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_models()
    else:
        pull_model(args.model)

import os
from huggingface_hub import HfApi
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("HF_TOKEN")
api = HfApi(token=TOKEN)

try:
    username = api.whoami()['name']
    print(f"Authentication successful as: {username}")
except Exception as e:
    print(f"Failed to authenticate with HuggingFace: {e}")
    exit(1)

repo_id = f"{username}/prod"
print(f"Creating HuggingFace Space: {repo_id}...")

try:
    api.create_repo(repo_id=repo_id, repo_type="space", space_sdk="docker", private=False, exist_ok=True)
except Exception as e:
    print(f"Warning: {e}")

# Push secrets from local .env
alchemy_key = os.getenv("ALCHEMY_API_KEY", "")
moralis_key = os.getenv("MORALIS_API_KEY", "")

print("Injecting secure API constraints...")
if alchemy_key:
    api.add_space_secret(repo_id=repo_id, key="ALCHEMY_API_KEY", value=alchemy_key)
if moralis_key:
    api.add_space_secret(repo_id=repo_id, key="MORALIS_API_KEY", value=moralis_key)

print("Uploading repository files safely (strict file filtering)...")
api.upload_folder(
    folder_path=".",
    repo_id=repo_id,
    repo_type="space",
    allow_patterns=[
        "app.py",
        "lp_reconciliation.ipynb",
        "requirements.txt",
        "README.md"
    ]
)

print(f"\n🎉 DEPLOYMENT SUCCESSFUL!")
print(f"Your dashboard is now building live at: https://huggingface.co/spaces/{repo_id}")

import json
import logging
import requests
from pathlib import Path
from typing import Dict, Any
from zipfile import ZipFile
from ..config import load_config
from ..crx import CrxDecoder
from ..console import console

logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.openai.com/v1").rstrip("/")
        self.model = config.get("model", "gpt-3.5-turbo")
        self.provider = config.get("provider", "openai")

    def chat_completion(self, prompt: str) -> str:
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert browser extension security analyst. Summarize the functionality and potential risks of the provided extension code."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            logger.error(f"AI API request failed: {e}")
            if response := getattr(e, "response", None):
                logger.error(f"Response: {response.text}")
            raise RuntimeError(f"AI API request failed: {e}")

def _read_file_snippet(zf: ZipFile, filename: str, max_lines: int = 50) -> str:
    try:
        with zf.open(filename) as f:
            content = f.read().decode("utf-8", errors="ignore")
            lines = content.splitlines()
            if len(lines) > max_lines:
                return "\n".join(lines[:max_lines]) + f"\n... (truncated, {len(lines) - max_lines} more lines)"
            return content
    except Exception:
        return "[Error reading file]"

def summarize_extension(file_path: Path, show_progress: bool = True) -> str:
    config = load_config()
    ai_config = config.get("ai", {})
    
    if not ai_config.get("enabled"):
        raise RuntimeError("AI analysis is disabled. Enable it in config.toml with `[ai] enabled = true`.")

    client = AIClient(ai_config)

    # Extract context
    context = []
    
    try:
        offset = 0
        if file_path.suffix.lower() == '.crx':
            offset = CrxDecoder.get_zip_offset(file_path)
            
        f = open(file_path, "rb")
        if offset > 0:
            f.seek(offset)
            
        with ZipFile(f) as zf:
            # 1. Manifest
            try:
                manifest_content = zf.read("manifest.json").decode("utf-8", errors="ignore")
                manifest = json.loads(manifest_content)
                context.append(f"## manifest.json\n```json\n{json.dumps(manifest, indent=2)}\n```")
            except Exception:
                return "Error: Could not read manifest.json"

            # 2. Identify interesting files
            files_to_read = []
            
            # Background scripts
            if "background" in manifest:
                bg = manifest["background"]
                if "scripts" in bg:
                    files_to_read.extend(bg["scripts"])
                if "service_worker" in bg:
                    files_to_read.append(bg["service_worker"])
            
            # Content scripts
            if "content_scripts" in manifest:
                for script in manifest["content_scripts"]:
                    if "js" in script:
                        files_to_read.extend(script["js"])
            
            # Limit to top 3 unique files to save tokens
            files_to_read = sorted(list(set(files_to_read)))[:3]

            for filename in files_to_read:
                if filename in zf.namelist():
                    snippet = _read_file_snippet(zf, filename)
                    context.append(f"## {filename}\n```javascript\n{snippet}\n```")

    except Exception as e:
        raise RuntimeError(f"Failed to read extension archive: {e}")
    finally:
        if 'f' in locals() and not f.closed:
            f.close()

    prompt = "Analyze the following browser extension files and provide a concise summary of what it does. Highlight any suspicious behavior or excessive permissions.\n\n" + "\n\n".join(context)

    if show_progress:
        with console.status("[bold green]Waiting for AI summary..."):
            return client.chat_completion(prompt)
    else:
        return client.chat_completion(prompt)

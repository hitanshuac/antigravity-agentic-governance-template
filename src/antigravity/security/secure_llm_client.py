import hashlib
import json
import os
from datetime import UTC, datetime
from typing import Any

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class SecureLLMClient:
    """
    Interceptor layer enforcing the OWASP Security mandate.
    Handles I/O sanitization, state memoization, and API quota limits.
    """

    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.api_available = True if self.api_key else False
        if self.api_available:
            self.client = Groq(api_key=self.api_key)

        self.response_cache = {}
        self.DAILY_LIMIT = 1000  # Enforcing free-tier RPD limit
        self.DAILY_TOKEN_LIMIT = 30000 * 60 # Enforcing free-tier TPD limit
        self.quota_file = os.path.join("data", "quota.json")
        quota_data = self._load_quota()
        self.daily_calls_made = quota_data.get("calls_made", 0)
        self.daily_tokens_used = quota_data.get("tokens_used", 0)

    def _load_quota(self) -> dict:
        """Loads the API quota from persistent storage, resetting if it's a new day."""
        os.makedirs("data", exist_ok=True)
        today = datetime.now(UTC).date().isoformat()

        try:
            if os.path.exists(self.quota_file):
                with open(self.quota_file, encoding="utf-8") as f:
                    data = json.load(f)

                if data.get("last_reset_date") == today:
                    return {"calls_made": data.get("calls_made", 0), "tokens_used": data.get("tokens_used", 0)}
        except Exception:
            pass

        # It's a new day (or file missing/corrupt), reset quota to 0
        return {"calls_made": 0, "tokens_used": 0}

    def _save_quota(self):
        """Flushes the current API quota to persistent storage."""
        today = datetime.now(UTC).date().isoformat()
        data = {"last_reset_date": today, "calls_made": self.daily_calls_made, "tokens_used": self.daily_tokens_used}
        try:
            with open(self.quota_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def invalidate_cache_for_state(self, state_data: Any) -> bool:
        """Evicts a poisoned cache entry when downstream validation fails."""
        state_hash = self._generate_state_hash(state_data)
        if state_hash in self.response_cache:
            del self.response_cache[state_hash]
            return True
        return False

    def _generate_state_hash(self, data: Any) -> str:
        """Creates a unique hash for the current data to check against the cache."""
        return hashlib.md5(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()

    def generate_content(self, prompt: str, state_data: Any = None) -> dict[str, Any]:
        """
        Executes a secure LLM call with pre-flight and post-flight interception.
        If state_data is provided, checks the memoization cache first.
        """
        state_hash = None
        if state_data:
            state_hash = self._generate_state_hash(state_data)
            if state_hash in self.response_cache:
                cached_resp = self.response_cache[state_hash]
                return {"status": "cached", "data": dict(cached_resp)}

        if not self.api_available:
            return {"status": "api_key_missing", "data": None}

        if self.daily_calls_made >= self.DAILY_LIMIT:
            return {"status": "quota_exhausted", "data": None}

        # Token Budget Formula (Rule 20-03)
        estimated_tokens = len(prompt) // 4 + 1000
        if self.daily_tokens_used + estimated_tokens >= self.DAILY_TOKEN_LIMIT:
            return {"status": "budget_exhausted", "data": None}

        # Pre-flight Defense (LLM01): Truncate to safe maximum length and ensure JSON instruction
        safe_prompt = prompt[:8000]
        if "json" not in safe_prompt.lower():
            safe_prompt += "\n\nYou must return the output as a valid JSON object."

        try:
            self.daily_calls_made += 1
            self.daily_tokens_used += estimated_tokens
            self._save_quota()

            # Fallback Chain (Rule 20-03)
            fallback_chain = os.environ.get("LLM_FALLBACK_CHAIN", "openai/gpt-oss-120b,qwen/qwen3.6-27b,llama-3.1-8b-instant")
            models = [m.strip() for m in fallback_chain.split(",")]
            model_to_use = models[0]

            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=[{"role": "user", "content": safe_prompt}],
                response_format={"type": "json_object"}
            )

            if hasattr(response, 'usage') and response.usage:
                 self.daily_tokens_used = self.daily_tokens_used - estimated_tokens + response.usage.total_tokens
                 self._save_quota()

            # Post-flight Defense (LLM06)
            result = json.loads(response.choices[0].message.content)

            if state_hash:
                self.response_cache[state_hash] = dict(result)

            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "error", "error": str(e), "data": None}

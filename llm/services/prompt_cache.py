import hashlib
from core.models import Prompt


def _compute_prompt_hash(prompt_type: str, prompt_text: str, scope: str | None = None) -> str:
    """Internal: consistent hash generator for prompt caching."""
    base = f"{scope or 'global'}::{prompt_type}::{prompt_text}".encode("utf-8")
    return hashlib.sha256(base).hexdigest()


def get_or_create_prompt_cache(user, prompt_text: str, prompt_type: str, scope: str | None = None):
    """
    Unified abstraction for caching LLM prompts and responses.
    Handles:
    - deterministic hashing
    - exact-match retrieval
    - creation of empty cache records if not found
    """
    hash_key = _compute_prompt_hash(prompt_type, prompt_text, scope)

    cached_prompt, created = Prompt.objects.get_or_create(
        user=user,
        hash=hash_key,
        type=prompt_type,
        defaults={
            "text": prompt_text,
            "llm_response": None,
            "is_mock": False,
        },
    )

    if not created:
        cached_prompt.used_count += 1
        cached_prompt.save(update_fields=["used_count"])

    return cached_prompt, created

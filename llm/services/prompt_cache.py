import hashlib
from core.models import Prompt


def _compute_prompt_hash(prompt_type: str, prompt_text: str, scope: str | None = None, ignore_time: bool = False) -> str:
    """Internal: consistent hash generator for prompt caching."""
    base = f"{scope or 'global'}::{prompt_type}::{prompt_text}".encode("utf-8")
    return hashlib.sha256(base).hexdigest()


def get_or_create_prompt_cache(user, prompt_text: str, prompt_type: str, scope: str | None = None, ignore_time: bool = False) -> tuple[Prompt, bool]:
    """
    Unified abstraction for caching LLM prompts and responses.
    Handles:
    - deterministic hashing
    - exact-match retrieval
    - creation of empty cache records if not found
    """
    """
    ignore_time: If True, removes any timestamps from prompt text before hashing.
    """
    text_to_hash = prompt_text
    if ignore_time:
        # Strip or normalize current time from prompt
        import re
        text_to_hash = re.sub(r"Current Time:.*", "Current Time: <ignored>", text_to_hash)
        text_to_hash = re.sub(r"Date:.*", "Date: <ignored>", text_to_hash)
        text_to_hash = re.sub(r"Approx. Remaining Hours Today:.*", "Approx. Remaining Hours Today: <ignored>", text_to_hash)
    hash_key = _compute_prompt_hash(prompt_type, text_to_hash, scope)

    cached_prompt, created = Prompt.objects.get_or_create(
        user=user,
        hash=hash_key,
        type=prompt_type,
        defaults={
            "text": prompt_text,
            "llm_response": None,
            "is_refined": False,
        },
    )

    if not created:
        cached_prompt.used_count += 1
        cached_prompt.save(update_fields=["used_count"])

    return cached_prompt, created

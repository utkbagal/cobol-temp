
import re

def mask_pii(text: str) -> str:
    # Mask phone numbers
    text = re.sub(r"\b\d{10}\b", "[PHONE]", text)

    # Mask emails
    text = re.sub(r"[A-Za-z0-9\._%+-]+@[A-Za-z0-9\.-]+\.[A-Z|a-z]{2,}", "[EMAIL]", text)

    # Mask policy numbers  (optional generic pattern)
    text = re.sub(r"POL\d+", "[POLICY_NO]", text)

    return text

import re

DOMAIN_REFUSAL = (
    "I'm designed to assist with coal mine governance, safety, "
    "compliance, inspections, and related information. "
    "I can't answer general or unrelated questions."
)

def is_coal_mine_related(user_message: str) -> bool:
    """
    Lightweight deterministic domain classifier.
    Returns False for obvious out-of-domain intents (jokes, general trivia, weather in arbitrary cities, etc).
    Returns True for in-domain or ambiguous intents, passing them to the LLM system prompt.
    """
    text = user_message.lower().strip()
    
    # 1. Explicitly reject generic "joke" or "story" requests even if they contain keywords
    if re.search(r"\bjoke(s)?\b", text) or re.search(r"\btell me a (story|poem)\b", text):
        return False
        
    # 2. Reject arbitrary code/game generation
    if re.search(r"\bwrite\s+(me\s+)?(a\s+)?(python|java|c\+\+|code|game)\b", text):
        return False
        
    # 3. Reject general trivia/history/sports patterns
    trivia_patterns = [
        r"who is the prime minister",
        r"capital of",
        r"won.*(cricket|football|soccer) match",
        r"who discovered",
        r"latest gk",
        r"quantum physics",
        r"quantum mechanics"
    ]
    for pattern in trivia_patterns:
        if re.search(pattern, text):
            return False
            
    # 4. Reject simple math
    if re.fullmatch(r"what is \d+\s*[\+\-\*\/]\s*\d+\??", text) or re.fullmatch(r"\d+\s*[\+\-\*\/]\s*\d+\??", text):
        return False
        
    # 5. Reject prompt injection attempts
    injection_patterns = [
        r"ignore (your |all )?(previous |prior )?instructions",
        r"you are now a",
        r"forget that you",
        r"system override",
        r"answer (this )?as (chatgpt|gpt|claude|gemini)",
        r"pretend you are",
        r"act as a general",
    ]
    for pattern in injection_patterns:
        if re.search(pattern, text):
            return False
    
    # 6. Reject entertainment / personal / politics
    misc_reject = [
        r"\b(movie|film) (story|plot|review)\b",
        r"\b(recipe|cooking)\b",
        r"\bhoroscope\b",
        r"\b(politics|election)\b",
        r"\bpersonal advice\b",
    ]
    for pattern in misc_reject:
        if re.search(pattern, text):
            return False

    # 7. Allow contextual questions ("what does this mean?", "how do i create a report?")
    if re.search(r"how do i", text) or re.search(r"what does this (mean|metric)", text) or re.search(r"summarize", text):
        return True
        
    # If it survived the negative filters, pass it to the LLM. 
    # The strong system prompt will act as the final domain guard.
    return True


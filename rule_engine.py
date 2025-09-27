def evaluate_prompt(prompt: str, costar: dict) -> tuple:
    if any(w in prompt.lower() for w in ["bomb", "kill", "attack"]):
        return "BLOCK", "Unsafe content detected", ""

    if len(prompt.split()) < 5:
        return "NEEDS_FIX", "Prompt too vague", "Please clarify your request."

    if costar["Tone"] in ["Emotional", "Polite", "Assertive"]:
        return "ALLOW", "Prompt is safe and expressive", ""

    return "ALLOW", "Prompt is safe and well-structured", ""
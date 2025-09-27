import spacy

nlp = spacy.load("en_core_web_sm")

def extract_costar(prompt: str) -> dict:
    doc = nlp(prompt)
    lower = prompt.lower()

    tone = "Neutral"
    if any(w in lower for w in ["excited", "amazing", "love", "hate", "angry", "sad"]):
        tone = "Emotional"
    elif any(p in lower for p in ["please", "kindly", "could you", "would you"]):
        tone = "Polite"
    elif any(p in lower for p in ["i need", "i want", "must", "should", "require"]):
        tone = "Assertive"

    return {
        "Context": ", ".join([ent.text for ent in doc.ents]) or "Unknown",
        "Objective": next((t.lemma_ for t in doc if t.pos_ == "VERB"), "Unknown"),
        "Style": "Formal" if any(t.text.lower() in ["therefore", "hence", "thus"] for t in doc) else "Casual",
        "Tone": tone,
        "Audience": "General" if "you" in lower else "Specialized",
        "Response": "Text" if any(w in lower for w in ["write", "explain", "describe"]) else "Unknown"
    }
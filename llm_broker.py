import requests

def get_llm_response(prompt, use_mock=True, model="mistral"):
    if use_mock:
        return f"[Mock Response] Based on your prompt: {prompt}"

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt},
            stream=True
        )

        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = line.decode("utf-8")
                    if chunk.startswith("{"):
                        data = eval(chunk)
                        full_response += data.get("response", "")
                except Exception:
                    continue

        return full_response or "[No response from LLM]"
    except requests.exceptions.ConnectionError:
        return "[Error] Ollama server is not running. Please start it using 'ollama serve'."
    except Exception as e:
        return f"[Error contacting LLM] {str(e)}"
from pathlib import Path
import re
import subprocess
import sys

DOCS = Path("docs")
MODEL = "mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit"


def tokenize(text):
    return set(re.findall(r"[a-zA-Z0-9_]+", text.lower()))


def retrieve(question, max_chunks=4):
    chunks = []

    for path in DOCS.glob("*.txt"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        paragraphs = [
            part.strip()
            for part in re.split(r"\\n\\s*\\n", text)
            if part.strip()
        ]

        for paragraph in paragraphs:
            if len(paragraph) > 1800:
                paragraph = paragraph[:1800]
            chunks.append((path.name, paragraph))

    q_tokens = tokenize(question)
    api_names = [
        "wait_time", "timeout", "start", "is_stopped",
        "paused", "autostart", "process_callback"
    ]
    scored = []

    for filename, chunk in chunks:
        lower_chunk = chunk.lower()
        score = len(q_tokens & tokenize(chunk))

        for api in api_names:
            if api in question.lower() and api in lower_chunk:
                score += 3

        if score:
            scored.append((score, filename, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[:max_chunks]

def main():
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        question = input("Godot question: ").strip()

    matches = retrieve(question)
    if not matches:
        print("No matching documentation found. Add relevant docs to docs/.")
        return

    context = "\n\n".join(
        f"[Source: {filename}]\n{chunk}"
        for _, filename, chunk in matches
    )

    prompt = f"""
You are GodotFix, a careful Godot 4 debugging assistant.

Rules:
- Ground API claims in the documentation excerpts below.
- Never invent methods, properties, signals, or enum names.
- The Timer documentation lists properties including wait_time,
  autostart, one_shot, paused, process_callback, and time_left.
- A Timer can be started with start() and emits timeout when its
  countdown finishes.
- If the excerpts do not support a claim, say so.
- Give three concise checks, a minimal working code example,
  and a verification step.

DOCUMENTATION:
{context}

QUESTION:
{question}

ANSWER:
"""

    print("\n--- Retrieved documentation ---")
    for score, filename, chunk in matches:
        print(f"\n[{filename} | keyword score {score}]")
        print(chunk[:700])

    print("\n--- GodotFix answer ---\n")
    subprocess.run(
        [
            "mlx_lm.generate",
            "--model", MODEL,
            "--prompt", prompt,
            "--max-tokens", "350",
        ],
        check=False,
    )


if __name__ == "__main__":
    main()

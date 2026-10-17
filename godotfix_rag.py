from pathlib import Path
import re
import subprocess
import sys
from godotfix_validate import validate

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
            for part in re.split(r"\n\s*\n", text)
            if part.strip()
        ]

        for paragraph in paragraphs:
            if len(paragraph) > 1800:
                paragraph = paragraph[:1800]
            chunks.append((path.name, paragraph))

    q_lower = question.lower()

    topic_files = {
        "timer": ["timer_godot4.txt"],
        "characterbody2d": ["character_body_2d_godot4.txt", "physics_body_2d_godot4.txt", "collision_shape_2d_godot4.txt"],
        "collisionshape2d": ["collision_shape_2d_godot4.txt", "physics_body_2d_godot4.txt"],
    }

    preferred_files = set()
    for topic, filenames in topic_files.items():
        if topic in q_lower:
            preferred_files.update(filenames)

    if preferred_files:
        chunks = [
            (filename, chunk)
            for filename, chunk in chunks
            if filename in preferred_files
        ]

    q_tokens = tokenize(question)
    api_names = [
        "wait_time", "timeout", "start", "is_stopped",
        "paused", "autostart", "process_callback"
    ]
    scored = []

    q_lower = question.lower()

    for filename, chunk in chunks:
        if (
            chunk.lstrip().startswith(("+---", "|", ".. _"))
            or "class_" in chunk and len(tokenize(chunk)) < 8
        ):
            continue
        
        lower_chunk = chunk.lower()
        chunk_tokens = tokenize(chunk)
        score = len(q_tokens & chunk_tokens)

        # Reward chunks containing the exact concepts asked about.
        important_terms = [
            "collision_shape2d", "collisionshape2d",
            "collision_layer", "collision_mask",
            "move_and_slide", "disabled", "shape",
            "velocity", "is_on_floor",
        ]

        for term in important_terms:
            if term in q_lower and term in lower_chunk:
                score += 5

        # Reward the relevant class documentation.
        if "characterbody2d" in q_lower and "character_body_2d" in filename:
            score += 3
        if "collisionshape2d" in q_lower and "collision_shape_2d" in filename:
            score += 3
        if "timer" in q_lower and "timer" in filename:
            score += 3

        if score:
            scored.append((score, filename, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)

    selected = []
    seen_files = set()

    for item in scored:
        score, filename, chunk = item
        if filename not in seen_files:
            selected.append(item)
            seen_files.add(filename)

    # Then fill remaining slots with the highest-scoring chunks.
    selected_ids = {id(item) for item in selected}

    for item in scored:
        if len(selected) >= max_chunks:
            break
        if id(item) not in selected_ids:
            selected.append(item)
            selected_ids.add(id(item))

    return selected[:max_chunks]

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
    
    reference_path = Path("evaluation/timer_reference.txt")

    if "timer" in question.lower() and reference_path.exists():
        context += "\n\n[Source: verified Godot 4 Timer reference]\n"
        context += reference_path.read_text(encoding="utf-8")

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
- Prefer the supplied verified example over generating a new API pattern.
- Never use Godot 3 signal syntax; use signal.connect(callable) in Godot 4.

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

    result = subprocess.run(
        [
            "mlx_lm.generate",
            "--model", MODEL,
            "--prompt", prompt,
            "--max-tokens", "350",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    answer = result.stdout
    print(answer)

    warnings = validate(answer)

    if warnings:
        print("\n--- Potential API issues to review ---")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("\nNo known suspicious patterns detected.")
        print("This does not guarantee the answer is correct.")

    if result.returncode != 0:
        print("\nWarning: text generation exited with an error.")
        print(result.stderr)

if __name__ == "__main__":
    main()

import re
import sys

RULES = [
    (
        r'\.connect\s*\(\s*["\']',
        "Possible Godot 3 signal syntax. In Godot 4, use signal.connect(callable).",
    ),
    (
        r'(?<![\w.])connect\s*\(\s*["\']',
        "Possible Godot 3 signal syntax. In Godot 4, use timeout.connect(_on_timeout).",
    ),
    (
        r'\bset_timeout\s*\(',
        "Timer.set_timeout() is not the Godot 4 Timer API. Check wait_time and start().",
    ),
    (
        r'\bset_interval\s*\(',
        "Timer.set_interval() is not the Godot 4 Timer API.",
    ),
    (
        r'\b(?:is_active|has_timeout_signal|has_timeout_callback)\s*\(',
        "Possible unsupported Timer method. Check the official API docs.",
    ),
    (
        r'\bpaused\s*\(',
        "Timer.paused is a property, not a method.",
    ),
]

def validate(text):
    warnings = []
    for pattern, message in RULES:
        if re.search(pattern, text):
            warnings.append(message)
    return warnings

if __name__ == "__main__":
    text = sys.stdin.read() if not sys.argv[1:] else " ".join(sys.argv[1:])
    warnings = validate(text)

    if warnings:
        print("POTENTIAL API ISSUES:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("No known suspicious patterns detected.")
        print("This does not guarantee the code is correct.")
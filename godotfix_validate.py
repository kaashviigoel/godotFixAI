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
    (
        r'\b(?:collision_shape2d|collision_shape)\.(?:collision_layer|collision_mask)\b',
        "Collision layers and masks belong to physics collision objects, not CollisionShape2D.",
    ),
    (
        r'\bPhysicsBody2D\.MODE_KINEMATIC\b|\bphysics_body2d\.mode\b',
        "This is not the correct Godot 4 CharacterBody2D setup. Check the official class docs.",
    ),
    (
        r'\bphysics_body2d\b',
        "Check whether physics_body2d is a real variable or node reference before using it.",
    ),
    (
        r'\bmove_and_slide\s*=\s*',
        "move_and_slide() is a method, not a Boolean property. Call move_and_slide().",
    ),
    (
        r'\b(?:self\.)?gravity\s*=',
        "CharacterBody2D has no built-in gravity property. Apply gravity through your script.",
    ),
    (
        r'\.set_shape\s*\(\s*Rect2\s*\(',
        "CollisionShape2D.shape expects a Shape2D resource, not a Rect2.",
    ),
    (
        r'\bmove_and_slide\b.{0,80}\bInspector\b',
        "move_and_slide() is a method, not an Inspector property.",
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
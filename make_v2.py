import json
import random
from pathlib import Path

examples = [
    # PHYSICS
    ("My CharacterBody2D falls through the floor.",
     "Check that the character and floor have enabled collision shapes, that the floor is a StaticBody2D or another suitable physics body, and that collision layers and masks overlap. Move the character through move_and_slide() in _physics_process(), not by directly changing position."),
    ("My player does not stop when touching a wall.",
     "Check that both bodies have valid collision shapes and compatible collision layers and masks. If the player is a CharacterBody2D, update velocity and call move_and_slide() in _physics_process()."),
    ("My character keeps falling even after I add gravity.",
     "CharacterBody2D does not apply gravity automatically. Apply gravity to velocity.y in _physics_process(), then call move_and_slide(). Check is_on_floor() to determine whether the character is grounded."),
    ("My character gets stuck inside the floor.",
     "Check that collision shapes do not start deeply overlapping, that the floor has a valid collision shape, and that movement uses move_and_slide() or move_and_collide(). Avoid repeatedly teleporting the character through colliders."),
    ("My player moves through walls when I change its position.",
     "Directly assigning position bypasses normal CharacterBody2D collision-aware movement. Update velocity and use move_and_slide() in _physics_process(), or use move_and_collide() when you need explicit collision handling."),
    ("My player cannot collide with a platform.",
     "Inspect the player's collision_mask and the platform's collision_layer. The player must scan a layer that includes the platform. Also verify that both have enabled, correctly positioned collision shapes."),
    # INPUT
    ("Input.is_action_just_pressed does not work.",
     "Open Project > Project Settings > Input Map and confirm the action exists and has the intended key or button assigned. Check spelling and capitalization in the script, and ensure the code runs while the node is active."),
    ("My player does not move when I press the arrow keys.",
     "Verify the input actions exist in Input Map and are assigned to the arrow keys. Check that the script is attached to an active node and that its input-handling code runs. Print the input result to diagnose the issue."),
    ("My jump button works only sometimes.",
     "Check that the jump action is correctly mapped and that the jump condition matches your intended behavior. For a grounded-only jump, use is_on_floor() and read just-pressed input in an appropriate input or physics callback."),
    ("The key works in the editor but not when the game runs.",
     "Check that the running game window has focus, the action is mapped in Project Settings > Input Map, and the script is attached to an active node. Add a print statement to confirm the input event is received."),
    ("My custom input action always returns false.",
     "Check the exact action name and capitalization in Project Settings > Input Map. Make sure at least one event is assigned and that the code queries the same action name."),
    ("How do I detect a key press once instead of every frame?",
     "Use Input.is_action_just_pressed(\"action_name\") to detect the frame an action begins. Use Input.is_action_pressed() when you want to detect that it remains held."),
    # NODE PATHS
    ("I get a Node not found error for $Sprite2D.",
     "Check the scene tree and confirm that a child named Sprite2D exists at that exact relative path. Node paths are case-sensitive. Update the path if the node was renamed or moved."),
    ("My @onready variable is null.",
     "Check that the node path resolves in the current scene and that the target exists when the script initializes. Use @onready var sprite = $Sprite2D for a direct child named Sprite2D, adjusting the path to match your scene."),
    ("I renamed a node and now my script breaks.",
     "Search scripts for references to the old node name, including $ paths, get_node() calls, and signal connections. Update each path to match the scene tree."),
    ("get_node throws an error when my scene starts.",
     "Verify that the requested path is correct relative to the node running the script and that the target exists at that time. Use get_node_or_null() if the node is genuinely optional, then handle a null result."),
    ("My instantiated enemy cannot find the player's node.",
     "Check whether the player exists in the active scene and whether the path is relative to the enemy or scene root. Consider assigning a player reference explicitly or using a group with get_first_node_in_group(). Handle cases where no player exists."),
    ("My scene works alone but breaks when instanced.",
     "Check assumptions about parent nodes, relative node paths, initialization order, and required exported references. An instanced scene may have a different parent or be created before its dependencies exist."),
    # SIGNALS
    ("My button's pressed signal does nothing.",
     "Select the button, inspect the Node > Signals panel, and confirm pressed is connected to the intended receiver and method. Check that the method name and arguments match and that the receiver is still in the scene."),
    ("I get an error saying a signal is already connected.",
     "Inspect existing signal connections before connecting again. Use is_connected() to check first, or connect the signal once during initialization rather than on every frame."),
    ("My signal callback never runs.",
     "Confirm the signal is emitted, the correct receiver method is connected, and the receiver exists. Check the signal name, method signature, and debugger output for connection errors."),
    ("How do I send a custom signal when an enemy dies?",
     "Declare a signal such as signal died, emit it with died.emit() when the enemy dies, and connect it to the receiver that should respond. Ensure the connection is made only once."),
    ("My signal callback receives the wrong number of arguments.",
     "Compare the signal's declared parameters with the callback method's parameters and any arguments supplied by the connection. Make their signatures compatible, then test the signal again."),
    ("A signal works once but not after changing scenes.",
     "Check whether the signal was connected to a node from the previous scene. Reconnect it to the new instance when appropriate, and avoid keeping stale references to nodes that have been freed."),
]

random.Random(42).shuffle(examples)

system = (
    "You are GodotFix, a careful Godot 4 debugging assistant. "
    "Give technically accurate, actionable steps. Do not invent Inspector properties. "
    "When the cause is uncertain, give checks rather than claiming certainty."
)

records = []
for prompt, answer in examples:
    records.append({
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": answer}
        ]
    })

out = Path("data/godotfix-v2")
out.mkdir(parents=True, exist_ok=True)

# 16 training examples, 4 validation examples, 4 held-out test examples
splits = {
    "train.jsonl": records[:16],
    "valid.jsonl": records[16:20],
    "test.jsonl": records[20:24],
}

for filename, rows in splits.items():
    with (out / filename).open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

print(f"Created {len(records)} examples in {out}")
for filename, rows in splits.items():
    print(f"{filename}: {len(rows)} examples")

import json
import random
from pathlib import Path

# Each example contains a realistic bug, a diagnosis, a fix,
# and a way to verify the result.
examples = [
    ("physics", "My CharacterBody2D falls through the floor.",
     "Check three things: both bodies have enabled CollisionShape2D nodes with valid shapes; the floor is a suitable physics body; and the player's collision_mask includes a layer used by the floor. For movement, update velocity in _physics_process() and call move_and_slide(). Test again with Debug > Visible Collision Shapes enabled."),

    ("physics", "My CharacterBody2D does not stop at walls.",
     "Check that both bodies have valid collision shapes and compatible collision layers and masks. Move the character using velocity and move_and_slide() in _physics_process(), rather than assigning position directly. Enable visible collision shapes to confirm the shapes overlap where expected."),

    ("physics", "My player never jumps.",
     "Check that the jump input action exists in Project Settings > Input Map, that the code runs, and that the player is grounded when the jump condition is evaluated. Example: if Input.is_action_just_pressed(\"jump\") and is_on_floor(): velocity.y = -400.0. Then call move_and_slide() in _physics_process()."),

    ("physics", "My character slides down a slope.",
     "Check floor detection and the CharacterBody2D floor settings, including floor_max_angle. Use move_and_slide() during _physics_process() and inspect is_on_floor() and velocity. Test on a simple slope with visible collision shapes before changing additional settings."),

    ("physics", "My player moves through walls when I set position.",
     "Directly assigning position bypasses normal collision-aware CharacterBody2D movement. Update velocity and call move_and_slide() in _physics_process(), or use move_and_collide() when you need explicit collision handling. Verify the collision shapes and layers as well."),

    ("input", "Input.is_action_just_pressed(\"jump\") always returns false.",
     "Check that jump exists in Project Settings > Input Map, that a key is assigned, and that the action name matches exactly. Add print(Input.is_action_pressed(\"jump\")) in a callback to check whether input is detected. If you use _input(), make sure the node is active and receives input."),

    ("input", "My player does not move with the arrow keys.",
     "Check the input actions and key bindings in Project Settings > Input Map. Confirm the script is attached to an active node and that its movement callback runs. Print the input values while pressing the keys, then check that velocity is updated and move_and_slide() is called."),

    ("input", "My jump triggers repeatedly while the key is held.",
     "Use Input.is_action_just_pressed(\"jump\") for a one-time press rather than Input.is_action_pressed(\"jump\"), which remains true while held. If jumping should only happen on the floor, also check is_on_floor()."),

    ("input", "My input works in the editor but not in the running game.",
     "Check that the game window has focus, the action is mapped in Input Map, and the running scene contains the node with the script. Add a print statement inside the callback to confirm it executes."),

    ("nodes", "I get a Node not found error for $Sprite2D.",
     "Inspect the scene tree and confirm that a child named Sprite2D exists at that exact relative path. Node paths are case-sensitive. Update the path if the node was renamed, moved, or placed under another node."),

    ("nodes", "My @onready variable is null.",
     "Check that the node path resolves from the node running the script and that the target exists when initialization occurs. For a direct child, use @onready var sprite: Sprite2D = $Sprite2D. Adjust the path to match the actual scene tree."),

    ("nodes", "My scene works alone but breaks when instanced.",
     "Check relative node paths, parent assumptions, required exported references, and initialization order. An instanced scene may have a different parent. Inspect the debugger for the first error and verify that dependencies exist before they are used."),

    ("nodes", "get_node throws an error when a node is missing.",
     "Verify that the path is relative to the node running the script and matches the scene tree. If the node is optional, use get_node_or_null() and check for null before accessing it. If it is required, fix the path or scene setup instead."),

    ("signals", "My button's pressed signal does nothing.",
     "Select the button and inspect Node > Signals to confirm pressed is connected to the intended receiver. Check that the receiver exists, the method name is correct, and its parameters match the signal. Add a print statement to the callback to test the connection."),

    ("signals", "My signal is already connected error appears.",
     "Check whether the signal is already connected before connecting it again. Use if not button.pressed.is_connected(_on_button_pressed): button.pressed.connect(_on_button_pressed). Connect it during initialization, not every frame."),

    ("signals", "My custom signal callback never runs.",
     "Confirm the signal is declared, emitted, and connected to a live receiver. Check spelling and callback parameters. Add a print immediately before emitting and inside the callback to find where execution stops."),

    ("scenes", "My change_scene_to_file call does not change scenes.",
     "Check that the path points to an existing scene file, such as res://scenes/level_2.tscn. Check the returned error code from get_tree().change_scene_to_file(path), and inspect the debugger for resource-loading errors."),

    ("scenes", "An instantiated enemy does not appear.",
     "Check that the PackedScene was loaded successfully, instantiate it, and add the instance to the active scene tree. For example: var enemy = preload(\"res://enemy.tscn\").instantiate(); get_tree().current_scene.add_child(enemy). Confirm its position is inside the visible area."),

    ("ui", "My Control node appears in the wrong place after resizing.",
     "Inspect the Control node's anchors, offsets, and parent container. Use layout presets appropriate to the intended position and test with different window sizes. If a Container controls the child, adjust the container layout rather than fighting its offsets."),

    ("ui", "My Label text is clipped.",
     "Check the Control node's size, text wrapping, clipping settings, and parent container. Increase the available space or enable appropriate wrapping and sizing. Test with the longest expected text and a different window size."),

    ("gdscript", "I get Invalid access to property or key on a base object of type Nil.",
     "A value being accessed is null. Inspect the exact line in the debugger, then verify the node path, variable assignment, and initialization order. Add a null check if the value is optional; otherwise fix the missing reference."),

    ("gdscript", "My function says too few arguments.",
     "Compare the function definition with every call site. Supply the required arguments in the correct order, or provide default values in the function definition if they are genuinely optional. Use the debugger's reported line to locate the failing call."),

    ("gdscript", "My timer timeout callback never fires.",
     "Confirm the Timer node exists, its wait_time is positive, and start() is called or autostart is enabled. Check that timeout is connected to the intended method and that the timer is not paused or stopped."),

    ("gdscript", "My array loop skips elements when I remove items.",
     "Removing elements while iterating forward can shift later elements and cause them to be skipped. Iterate backward when removing by index, or build a separate collection of items to remove and process it after the loop."),

    ("resources", "My texture is missing when I run the game.",
     "Check that the resource path is correct, the file exists, and the texture reference is assigned. Inspect the debugger for import or loading errors. If loading by path in code, confirm it uses the correct res:// path."),

    ("resources", "My exported Node reference is empty in the Inspector.",
     "Confirm the exported variable's type matches the node or resource you intend to assign. Select the correct scene instance and assign the reference in the Inspector. Check that the running instance is the one you configured."),

    ("animation", "My AnimationPlayer animation does not play.",
     "Confirm the AnimationPlayer contains an animation with the exact name, the node path tracks resolve, and play() is called on the intended AnimationPlayer. Check whether another animation or script immediately overrides the same properties."),

    ("animation", "My sprite animation stays on the first frame.",
     "Check that the SpriteFrames resource contains multiple frames, the intended animation name is correct, and play() is called. Confirm the animation speed is nonzero and the node is not immediately stopped by another script."),

    ("audio", "My sound effect does not play.",
     "Check that the AudioStreamPlayer has a valid stream assigned and that play() is called. Inspect the output bus, volume, mute state, and debugger for resource errors. Test with a known working audio file."),

    ("ui", "My button cannot be clicked.",
     "Check that the button is visible, enabled, and inside the viewport. Inspect whether another Control node intercepts mouse input and review mouse_filter settings on overlapping controls. Connect pressed and test with a print statement."),

    ("physics", "My Area2D does not detect the player.",
     "Check that the Area2D has a valid CollisionShape2D, monitoring is enabled, and its collision_mask includes a layer used by the player. Connect body_entered for physics bodies or area_entered for other areas, depending on what should be detected."),

    ("nodes", "My group lookup returns null.",
     "Confirm the target node belongs to the exact group name and is already in the scene tree when the lookup occurs. Check spelling and capitalization. Handle an empty result instead of assuming a matching node exists."),

    ("gdscript", "My variable is not updated inside a function.",
     "Inspect variable scope and confirm that the function changes the intended variable rather than creating a local variable with the same name. Print the value before and after the assignment and check whether another callback resets it."),

    ("scenes", "My game freezes after adding many enemies.",
     "Profile the running scene before guessing at the cause. Check expensive per-frame work, repeated resource loading, large numbers of physics objects, and excessive node processing. Use the profiler to identify the actual bottleneck, then optimize that area."),

    ("physics", "My CharacterBody2D jitters while moving on the floor.",
     "Check whether movement is applied in more than one callback, whether velocity is updated consistently in _physics_process(), and whether the character collides with overlapping or uneven shapes. Use move_and_slide() once per physics update and test on a simple flat floor."),

    ("physics", "My CharacterBody2D reports is_on_floor() as false.",
     "Check that move_and_slide() runs before the floor-state check, that the floor has a valid collision shape, and that the floor angle is within floor_max_angle. Inspect the collision shapes and test on a simple flat floor."),

    ("signals", "A signal fires twice when I click once.",
     "Check for duplicate signal connections or code that connects the same callback multiple times. Inspect the Signals panel and use is_connected() before connecting. Add a print to the callback to confirm how many times it executes."),

    ("input", "My mouse click is not detected by a Control node.",
     "Check that the Control node is visible, enabled, and not covered by another control that intercepts mouse input. Review mouse_filter and confirm the correct input signal or callback is being used."),

    ("resources", "preload reports that a resource cannot be loaded.",
     "Verify the exact res:// path and filename capitalization, and confirm the resource exists in the project. Check the file type and debugger output. Fix the path or import issue before changing unrelated code."),

    ("gdscript", "I get a parser error after adding a typed variable.",
     "Inspect the reported line and the line before it for missing colons, indentation errors, or invalid type syntax. Compare the declaration with valid GDScript 2 syntax and fix the first parser error before addressing later errors."),
]

# Split deterministically so the held-out evaluation is not trained on.
random.Random(2026).shuffle(examples)
train = examples[:28]
valid = examples[28:34]
test = examples[34:]

system = (
    "You are GodotFix, a careful Godot 4 debugging assistant. "
    "Give technically accurate, concise, actionable answers. "
    "Do not invent Inspector properties. Do not claim a cause without evidence. "
    "When asked for checks and a fix, provide numbered checks, a minimal relevant fix, "
    "and a verification step. If the cause is uncertain, say what to inspect."
)

def record(row):
    category, prompt, answer = row
    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": f"[{category}] {prompt}"},
            {"role": "assistant", "content": answer},
        ]
    }

out = Path("data/godotfix-v3")
out.mkdir(parents=True, exist_ok=True)

for filename, rows in [
    ("train.jsonl", train),
    ("valid.jsonl", valid),
    ("test.jsonl", test),
]:
    with (out / filename).open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(record(row), ensure_ascii=False) + "\n")

print(f"Created {len(examples)} examples in {out}")
print(f"Train: {len(train)} | Validation: {len(valid)} | Test: {len(test)}")
print("Existing datasets and adapters were not changed.")

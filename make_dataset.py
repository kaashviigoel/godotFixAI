
import json
from pathlib import Path

# Each example teaches the model to diagnose a Godot 4 problem
# and return a cause, fix, and verification step.
examples = [
    {
        "prompt": "My CharacterBody2D won't jump when I press Space.",
        "answer": "CAUSE: The jump input may not be configured or detected.\nFIX: Add a jump action in Project Settings > Input Map and bind Space. Check Input.is_action_just_pressed(\"jump\") in _physics_process().\nVERIFY: Confirm the action name matches and that the player can jump when grounded."
    },
    {
        "prompt": "My player falls through the floor.",
        "answer": "CAUSE: Collision shapes may be missing, disabled, or incorrectly positioned.\nFIX: Check that the player and floor have appropriate CollisionShape2D nodes and compatible collision layers and masks.\nVERIFY: Enable Visible Collision Shapes while running the scene and inspect the shapes."
    },
    {
        "prompt": "Godot says Node not found when I call get_node(\"Camera2D\").",
        "answer": "CAUSE: The node path may not match the scene tree.\nFIX: Inspect the Remote or Local scene tree and use the correct relative path, such as $Camera2D if it is a direct child.\nVERIFY: Run the scene and confirm the node exists at that path."
    },
    {
        "prompt": "My button's pressed signal doesn't call my function.",
        "answer": "CAUSE: The signal may not be connected, or the callback may be incorrect.\nFIX: Connect Button.pressed to the intended method using the Node dock or a correct code connection.\nVERIFY: Add a temporary print statement to the callback and click the button."
    },
    {
        "prompt": "My player moves but ignores gravity.",
        "answer": "CAUSE: Gravity may not be applied to velocity, or movement may not use the physics update correctly.\nFIX: In _physics_process(delta), apply gravity to velocity.y when not on the floor, then call move_and_slide().\nVERIFY: Confirm gravity is applied each physics frame and the floor collision works."
    },
    {
        "prompt": "My Sprite2D is invisible.",
        "answer": "CAUSE: The texture may be missing, the node may be hidden, or its modulation alpha may be zero.\nFIX: Check the Texture property, Visible setting, modulate alpha, and position.\nVERIFY: Inspect the running scene and confirm the sprite has a valid texture and visible alpha."
    },
    {
        "prompt": "My health bar does not update after the player takes damage.",
        "answer": "CAUSE: The health value may change without updating the UI.\nFIX: Update the ProgressBar.value when health changes, or connect a health_changed signal to the UI update method.\nVERIFY: Print the health value and ProgressBar.value after damage."
    },
    {
        "prompt": "My enemy keeps moving through a wall.",
        "answer": "CAUSE: Collision configuration or the movement method may be incorrect.\nFIX: Check collision shapes, collision layers and masks, and use an appropriate physics body and movement method.\nVERIFY: Show collision shapes and test the enemy against a simple static wall."
    },
    {
        "prompt": "I get Invalid get index on a null instance.",
        "answer": "CAUSE: A variable expected to reference an object is null.\nFIX: Check where the reference is assigned and confirm the node or resource exists before accessing its properties.\nVERIFY: Add a null check and print the reference immediately before the failing line."
    },
    {
        "prompt": "My animation never plays.",
        "answer": "CAUSE: The animation name, player reference, or playback call may be incorrect.\nFIX: Confirm the AnimationPlayer reference and exact animation name, then call play() on the intended animation.\nVERIFY: Inspect the animation list and check whether playback starts at runtime."
    },
    {
        "prompt": "My projectile spawns but never moves.",
        "answer": "CAUSE: Its velocity may not be initialized or applied during physics updates.\nFIX: Set the projectile's direction and speed when spawning it, then update its position or velocity in the appropriate physics method.\nVERIFY: Print its velocity and observe its position across multiple physics frames."
    },
    {
        "prompt": "My scene transition fails.",
        "answer": "CAUSE: The scene path may be invalid, or the scene may fail to load.\nFIX: Check the scene file path and use get_tree().change_scene_to_file() with the correct path.\nVERIFY: Check the returned error and confirm the target scene exists."
    },
    {
        "prompt": "My input action jump works in the editor but not in the exported game.",
        "answer": "CAUSE: The exported project may have different settings or the action may not be configured as expected.\nFIX: Inspect the Input Map and exported project settings, then reproduce the issue in a clean export.\nVERIFY: Log the action state in the exported build and compare it with the editor."
    },
    {
        "prompt": "My character slides down a slope when it should stand still.",
        "answer": "CAUSE: Gravity, floor detection, or floor stopping behavior may be contributing to movement.\nFIX: Inspect floor_max_angle, floor snapping, gravity handling, and whether velocity is reset appropriately when grounded.\nVERIFY: Test on a simple slope and inspect is_on_floor() and velocity."
    },
    {
        "prompt": "My enemy's death signal never reaches the level manager.",
        "answer": "CAUSE: The signal may not be connected to the intended receiver or may never be emitted.\nFIX: Verify the signal declaration, emission point, and connection target.\nVERIFY: Add temporary print statements at emission and callback entry."
    },
    {
        "prompt": "My camera follows the player with a huge delay.",
        "answer": "CAUSE: Camera smoothing or a custom follow calculation may be introducing delay.\nFIX: Inspect position smoothing settings and any interpolation in the follow script.\nVERIFY: Disable smoothing temporarily and compare the camera response."
    },
    {
        "prompt": "My inventory opens but the items do not appear.",
        "answer": "CAUSE: The inventory UI may not be receiving the item data or refreshing its display.\nFIX: Check the data source and update the item container when inventory contents change.\nVERIFY: Print the inventory contents and confirm the UI receives the expected items."
    },
    {
        "prompt": "My Area2D never detects the player.",
        "answer": "CAUSE: Monitoring, collision shapes, or collision masks may be incorrect.\nFIX: Check monitoring, the player's collision layer, the Area2D mask, and overlapping shapes.\nVERIFY: Connect body_entered temporarily and test with visible collision shapes."
    },
    {
        "prompt": "My timer timeout callback never runs.",
        "answer": "CAUSE: The timer may not be started, may be paused, or may have no valid timeout connection.\nFIX: Check wait_time, autostart or start(), pause state, and the timeout signal connection.\nVERIFY: Print when the timer starts and when the timeout callback executes."
    },
    {
        "prompt": "My scene has two players after I restart the level.",
        "answer": "CAUSE: The previous player may not be removed, or the new scene may spawn another player.\nFIX: Inspect scene reload logic and any persistent nodes that spawn players.\nVERIFY: Print player instance IDs after restarting and check the scene tree."
    },
    {
        "prompt": "My GDScript says Identifier not found: score.",
        "answer": "CAUSE: The variable may be undeclared or outside the current scope.\nFIX: Declare score in the appropriate script or pass it through a valid reference.\nVERIFY: Check spelling, scope, and whether the script containing score is attached to the expected node."
    },
    {
        "prompt": "My rigid body does not respond to impulses.",
        "answer": "CAUSE: The body may be frozen, have incorrect settings, or receive the impulse at the wrong time.\nFIX: Check freeze and physics settings and apply the impulse to the intended RigidBody2D or RigidBody3D.\nVERIFY: Print the body's state and test with a simple impulse in a running scene."
    },
    {
        "prompt": "My UI label shows the old score.",
        "answer": "CAUSE: The displayed label is not refreshed when the score changes, or the wrong label is referenced.\nFIX: Update the label text after changing the score and verify the node reference.\nVERIFY: Print the score and label text after each scoring event."
    },
    {
        "prompt": "My custom signal gives an argument count error.",
        "answer": "CAUSE: The signal's declared arguments and connected callback parameters may not match.\nFIX: Compare the signal declaration, emit_signal arguments, and callback signature.\nVERIFY: Emit a test signal and confirm each expected argument arrives."
    },
]

from sklearn.model_selection import train_test_split

labels = [row["answer"].split("\n")[0] for row in examples]
# Split by the original example order's category blocks.
# Each category has six examples.
categories = (
    ["input"] * 6
    + ["physics"] * 6
    + ["node_path"] * 6
    + ["signals"] * 6
)

train_rows, remaining, train_labels, remaining_labels = train_test_split(
    examples,
    categories,
    test_size=8,
    random_state=42,
    stratify=categories,
)

valid_rows, test_rows, _, _ = train_test_split(
    remaining,
    remaining_labels,
    test_size=4,
    random_state=42,
    stratify=remaining_labels,
)

splits = {
    "train": train_rows,
    "valid": valid_rows,
    "test": test_rows,
}

root = Path("data/godotfix")
root.mkdir(parents=True, exist_ok=True)

for split_name, rows in splits.items():
    path = root / f"{split_name}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            record = {
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are GodotFix, a careful Godot 4 debugging "
                            "assistant. Do not invent project details. "
                            "Use CAUSE, FIX, and VERIFY sections."
                        ),
                    },
                    {"role": "user", "content": row["prompt"]},
                    {"role": "assistant", "content": row["answer"]},
                ]
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"{split_name}: {len(rows)} examples -> {path}")

print("\nDataset created.")

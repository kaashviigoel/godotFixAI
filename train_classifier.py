
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

# Tiny starter dataset: 40 labeled Godot bug descriptions.
examples = [
    # Input problems
    ("Space key does nothing when I try to jump", "input"),
    ("Input.is_action_just_pressed does not trigger", "input"),
    ("My character cannot move when I press the arrow keys", "input"),
    ("The jump button is not responding", "input"),
    ("The input action name does not match the Input Map", "input"),
    ("Keyboard input works in one scene but not another", "input"),
    ("My attack key is not detected by the game", "input"),
    ("The player cannot sprint using the shift key", "input"),
    ("Mouse clicks are not detected by my game", "input"),
    ("The interact button does not work", "input"),

    # Physics and movement problems
    ("CharacterBody2D falls through the floor", "physics"),
    ("My player slides forever after moving", "physics"),
    ("velocity does not move my character", "physics"),
    ("The player ignores gravity", "physics"),
    ("move_and_slide does not work as expected", "physics"),
    ("My character gets stuck on slopes", "physics"),
    ("RigidBody2D passes through a wall", "physics"),
    ("The collision shape does not stop the player", "physics"),
    ("My platform moves but the player falls off", "physics"),
    ("The enemy keeps bouncing uncontrollably", "physics"),

    # Node path and reference problems
    ("Node not found when I use get_node", "node_path"),
    ("My script cannot find the Sprite2D child", "node_path"),
    ("I get a null instance when accessing a node", "node_path"),
    ("The path to my player node is incorrect", "node_path"),
    ("get_node returns nothing for my UI label", "node_path"),
    ("The node reference is null in my script", "node_path"),
    ("I renamed a node and the script stopped working", "node_path"),
    ("The scene tree path does not point to my camera", "node_path"),
    ("Cannot access the child node from this script", "node_path"),
    ("The node reference is missing after changing scenes", "node_path"),

    # Signals and event problems
    ("My button pressed signal does not fire", "signals"),
    ("The signal is not connected to my function", "signals"),
    ("A signal callback is never called", "signals"),
    ("My enemy death signal does not reach the UI", "signals"),
    ("The button click does not run its connected method", "signals"),
    ("I connected the same signal twice by mistake", "signals"),
    ("The health changed signal does not update the label", "signals"),
    ("My custom signal is emitted but nothing happens", "signals"),
    ("The receiver function has the wrong signal arguments", "signals"),
    ("How do I connect a signal between two nodes", "signals"),
]

X = [text for text, label in examples]
y = [label for text, label in examples]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
    ("classifier", LogisticRegression(max_iter=1000)),
])

print(f"Training on {len(X_train)} examples...")
model.fit(X_train, y_train)

predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(f"\nTest accuracy: {accuracy:.1%}")
print("\nClassification report:")
print(classification_report(y_test, predictions, zero_division=0))

output_dir = Path("models")
output_dir.mkdir(exist_ok=True)
joblib.dump(model, output_dir / "godotfix_classifier.joblib")

print("\nSaved trained model to models/godotfix_classifier.joblib")

print("\nTry some predictions:")
for question in [
    "My jump key does nothing",
    "My character falls through the ground",
    "Godot cannot find my camera node",
    "My button signal never fires",
]:
    print(f"{question} -> {model.predict([question])[0]}")

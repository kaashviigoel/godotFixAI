
import joblib
from pathlib import Path

model_path = Path("models/godotfix_classifier.joblib")

if not model_path.exists():
    raise FileNotFoundError(
        "Trained model not found. Run python train_classifier.py first."
    )

model = joblib.load(model_path)

print("GodotFix AI v0.1")
print("Describe a Godot bug, or type 'quit' to exit.\n")

while True:
    question = input("Bug > ").strip()

    if question.lower() in {"quit", "exit"}:
        print("GG. See you next time!")
        break

    if not question:
        continue

    prediction = model.predict([question])[0]
    probabilities = model.predict_proba([question])[0]
    confidence = max(probabilities)

    print(f"Predicted category: {prediction}")
    print(f"Model confidence: {confidence:.1%}\n")

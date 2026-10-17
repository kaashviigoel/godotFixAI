import json
import re
import subprocess
import sys
from pathlib import Path

CASE = Path("evaluation/cases/characterbody2d_floor.json")
MODEL = "mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit"

case = json.loads(CASE.read_text(encoding="utf-8"))
question = case["question"]

print("Generating answer...")
result = subprocess.run(
    [sys.executable, "-c",
     "import subprocess, sys; "
     "r=subprocess.run(['mlx_lm.generate','--model',sys.argv[1],"
     "'--prompt',sys.argv[2],'--max-tokens','350'],"
     "capture_output=True,text=True); "
     "print(r.stdout); "
     "sys.exit(r.returncode)",
     MODEL, question],
    capture_output=True,
    text=True,
)

answer = result.stdout

if result.returncode != 0 or not answer.strip():
    print("Generation failed:")
    print(result.stderr or answer)
    raise SystemExit(1)

print("\n--- GENERATED ANSWER ---\n")
print(answer)

lower = answer.lower()
required = case["required_concepts"]
forbidden = case["forbidden_patterns"]

print("\n--- AUTOMATED CHECKS ---")
missing = [term for term in required if term.lower() not in lower]
hits = [pattern for pattern in forbidden if pattern.lower() in lower]

print(f"Required concepts present: {len(required) - len(missing)}/{len(required)}")
print("\n--- RESULT ---")

if missing or hits:
    print("FAIL: answer missed required concepts or used forbidden patterns.")
else:
    print("PASS: keyword checks passed; manual correctness review is still required.")

print("\nReference checks for manual review:")
for item in case["reference_checks"]:
    print("-", item)
import os

os.environ["PYTHONPATH"] = "src"

steps = [
    f"python src/import_data.py",
    f"python src/prepare_data.py",
    f"python src/train_model.py",
    f"python src/service.py"
]

for step in steps:
    print(f"\n Start: {step}")
    if os.system(step) != 0:
        print(f" Error at: {step}")
        break
    else:
        print(f" Finished: {step}")

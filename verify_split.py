# verify_split.py
import os

paths = {
    'Train Images': 'datasets/images/train',
    'Train Labels': 'datasets/labels/train',
    'Val Images': 'datasets/images/val',
    'Val Labels': 'datasets/labels/val'
}

print("📊 Dataset Verification:\n")

for name, path in paths.items():
    if os.path.exists(path):
        count = len([f for f in os.listdir(path) if not f.startswith('.')])
        print(f"✓ {name:15} : {count:3} files")
    else:
        print(f"✗ {name:15} : NOT FOUND")

print("\n✅ Ready to train!")
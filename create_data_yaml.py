# create_data_yaml.py
import os

current_dir = os.getcwd().replace('\\', '/')
dataset_path = f"{current_dir}/datasets"

yaml_content = f"""# YOLOv8 Dataset Configuration
path: {dataset_path}
train: images/train
val: images/val

# Classes
nc: 9
names:
  0: Disk Driver
  1: Image
  2: Notification
  3: Search box
  4: Search button
  5: Video
  6: WhatsApp Message box
  7: WhatsApp Send Button
  8: WhatsApp person
"""

output_file = 'datasets/data.yaml'
with open(output_file, 'w') as f:
    f.write(yaml_content)

print(f"✅ Created: {output_file}\n")
print("Content:")
print(yaml_content)
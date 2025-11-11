# split_dataset.py
import os
import shutil
from pathlib import Path
import random

def split_dataset(images_dir='datasets/images', 
                  labels_dir='datasets/labels', 
                  train_ratio=0.8):
    """
    Split dataset into train and val folders
    train_ratio: 0.8 means 80% train, 20% validation
    """
    
    print("📂 Splitting dataset into train/val...")
    print(f"   Train: {train_ratio*100:.0f}%")
    print(f"   Val: {(1-train_ratio)*100:.0f}%\n")
    
    # Create directory structure
    dirs_to_create = [
        f'{images_dir}/train',
        f'{images_dir}/val',
        f'{labels_dir}/train',
        f'{labels_dir}/val'
    ]
    
    for dir_path in dirs_to_create:
        os.makedirs(dir_path, exist_ok=True)
    
    # Get all image files
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
        image_files.extend(Path(images_dir).glob(ext))
    
    # Filter out files already in train/val subdirs
    image_files = [f for f in image_files if f.parent.name == 'images']
    
    if not image_files:
        print("❌ No images found in datasets/images/")
        print("   Make sure your images are directly in 'datasets/images/' folder")
        return
    
    print(f"✓ Found {len(image_files)} images")
    
    # Shuffle for random split
    random.seed(42)  # For reproducibility
    random.shuffle(image_files)
    
    # Calculate split point
    split_idx = int(len(image_files) * train_ratio)
    train_images = image_files[:split_idx]
    val_images = image_files[split_idx:]
    
    print(f"✓ Train set: {len(train_images)} images")
    print(f"✓ Val set: {len(val_images)} images\n")
    
    # Move files
    def move_files(file_list, subset_name):
        moved_images = 0
        moved_labels = 0
        missing_labels = []
        
        for img_path in file_list:
            img_name = img_path.name
            label_name = img_path.stem + '.txt'
            
            # Source paths
            src_img = img_path
            src_label = Path(labels_dir) / label_name
            
            # Destination paths
            dst_img = Path(images_dir) / subset_name / img_name
            dst_label = Path(labels_dir) / subset_name / label_name
            
            # Move image
            shutil.move(str(src_img), str(dst_img))
            moved_images += 1
            
            # Move label if exists
            if src_label.exists():
                shutil.move(str(src_label), str(dst_label))
                moved_labels += 1
            else:
                missing_labels.append(img_name)
        
        print(f"{subset_name.upper()}:")
        print(f"  ✓ Moved {moved_images} images")
        print(f"  ✓ Moved {moved_labels} labels")
        
        if missing_labels:
            print(f"  ⚠️  {len(missing_labels)} images missing labels:")
            for name in missing_labels[:5]:  # Show first 5
                print(f"     - {name}")
            if len(missing_labels) > 5:
                print(f"     ... and {len(missing_labels)-5} more")
        print()
    
    # Move train files
    move_files(train_images, 'train')
    
    # Move val files
    move_files(val_images, 'val')
    
    print("✅ Dataset split complete!")
    print("\n📁 Final structure:")
    print("datasets/")
    print("├── images/")
    print(f"│   ├── train/  ({len(train_images)} images)")
    print(f"│   └── val/    ({len(val_images)} images)")
    print("├── labels/")
    print(f"│   ├── train/  ({len(train_images)} labels)")
    print(f"│   └── val/    ({len(val_images)} labels)")
    print("└── data.yaml")

if __name__ == "__main__":
    # Check current structure
    print("📋 Current structure:")
    
    if os.path.exists('datasets/images'):
        img_files = list(Path('datasets/images').glob('*.*'))
        img_files = [f for f in img_files if f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
        print(f"   Images: {len(img_files)} files in datasets/images/")
    else:
        print("   ❌ datasets/images/ not found")
    
    if os.path.exists('datasets/labels'):
        label_files = list(Path('datasets/labels').glob('*.txt'))
        print(f"   Labels: {len(label_files)} files in datasets/labels/")
    else:
        print("   ❌ datasets/labels/ not found")
    
    print("\n" + "="*60)
    
    # Run the split
    split_dataset(
        images_dir='datasets/images',
        labels_dir='datasets/labels',
        train_ratio=0.8  # 80% train, 20% validation
    )
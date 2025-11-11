# split_dataset_fixed.py
import os
import shutil
from pathlib import Path
import random

def split_dataset(images_dir='datasets/images', 
                  labels_dir='datasets/labels', 
                  train_ratio=0.8):
    """
    Split dataset into train and val folders
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
        print(f"✓ Created: {dir_path}")
    
    print()
    
    # Get all files directly in images folder (not in subdirectories)
    images_path = Path(images_dir)
    
    # Get only files (not directories) with image extensions
    all_files = []
    for item in images_path.iterdir():
        if item.is_file() and item.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
            all_files.append(item)
    
    if not all_files:
        print("❌ No images found in datasets/images/")
        print("   Make sure your images are directly in 'datasets/images/' folder")
        return
    
    # Remove duplicates (just in case)
    image_files = list(set(all_files))
    
    print(f"✓ Found {len(image_files)} unique images")
    
    # Shuffle for random split
    random.seed(42)
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
        errors = []
        
        for img_path in file_list:
            try:
                img_name = img_path.name
                label_name = img_path.stem + '.txt'
                
                # Source paths
                src_img = img_path
                src_label = Path(labels_dir) / label_name
                
                # Destination paths
                dst_img = Path(images_dir) / subset_name / img_name
                dst_label = Path(labels_dir) / subset_name / label_name
                
                # Check if source image exists
                if not src_img.exists():
                    errors.append(f"Image not found: {img_name}")
                    continue
                
                # Move image
                shutil.copy2(str(src_img), str(dst_img))
                moved_images += 1
                
                # Move label if exists
                if src_label.exists():
                    shutil.copy2(str(src_label), str(dst_label))
                    moved_labels += 1
                else:
                    missing_labels.append(img_name)
                    
            except Exception as e:
                errors.append(f"{img_name}: {str(e)}")
        
        print(f"{subset_name.upper()}:")
        print(f"  ✓ Copied {moved_images} images")
        print(f"  ✓ Copied {moved_labels} labels")
        
        if missing_labels:
            print(f"  ⚠️  {len(missing_labels)} images missing labels:")
            for name in missing_labels[:5]:
                print(f"     - {name}")
            if len(missing_labels) > 5:
                print(f"     ... and {len(missing_labels)-5} more")
        
        if errors:
            print(f"  ❌ {len(errors)} errors:")
            for err in errors[:5]:
                print(f"     - {err}")
        
        print()
        
        return moved_images, moved_labels
    
    # Copy train files
    train_imgs, train_lbls = move_files(train_images, 'train')
    
    # Copy val files
    val_imgs, val_lbls = move_files(val_images, 'val')
    
    print("✅ Dataset split complete!")
    print("\n📁 Final structure:")
    print("datasets/")
    print("├── images/")
    print(f"│   ├── train/  ({train_imgs} images)")
    print(f"│   └── val/    ({val_imgs} images)")
    print("├── labels/")
    print(f"│   ├── train/  ({train_lbls} labels)")
    print(f"│   └── val/    ({val_lbls} labels)")
    print("└── data.yaml")
    
    print("\n💡 Original files are still in datasets/images/ and datasets/labels/")
    print("   You can delete them after verifying the split worked correctly")

if __name__ == "__main__":
    # Check current structure
    print("📋 Current structure:")
    
    images_path = Path('datasets/images')
    if images_path.exists():
        img_files = [f for f in images_path.iterdir() 
                     if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']]
        print(f"   Images: {len(img_files)} files in datasets/images/")
    else:
        print("   ❌ datasets/images/ not found")
    
    labels_path = Path('datasets/labels')
    if labels_path.exists():
        label_files = [f for f in labels_path.iterdir() 
                       if f.is_file() and f.suffix == '.txt']
        print(f"   Labels: {len(label_files)} files in datasets/labels/")
    else:
        print("   ❌ datasets/labels/ not found")
    
    print("\n" + "="*60)
    
    # Run the split
    split_dataset(
        images_dir='datasets/images',
        labels_dir='datasets/labels',
        train_ratio=0.8
    )
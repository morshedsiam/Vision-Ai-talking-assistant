# train_custom_yolo.py
from ultralytics import YOLO
import torch

def train_model():
    """Training function"""
    print("="*60)
    print("🚀 TRAINING YOLOV8N ON SCREEN ELEMENTS")
    print("="*60)

    # Check GPU
    print(f"\n💻 GPU Info:")
    print(f"CUDA: {torch.cuda.is_available()}")
    print(f"Device: {torch.cuda.get_device_name(0)}")
    print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB\n")

    # Load base model
    print("📦 Loading YOLOv8n pretrained weights...")
    model = YOLO('yolov8n.pt')

    # Training config
    print("⚙️  Training Configuration:")
    print("   Dataset: datasets/data.yaml")
    print("   Epochs: 100")
    print("   Batch Size: 16")
    print("   Image Size: 640x640")
    print("   Device: GPU (RTX 2060)")
    print("   Classes: 9 screen elements\n")

    print("🏋️  Starting training (this will take ~15-20 minutes)...\n")

    # Train
    results = model.train(
        data='datasets/data.yaml',
        epochs=100,
        imgsz=640,
        batch=16,
        device=0,
        workers=0,  # Changed from 4 to 0 to avoid multiprocessing issues
        project='runs/train',
        name='screen_detector_v1',
        patience=20,
        save=True,
        save_period=10,
        plots=True,
        verbose=True,
        lr0=0.01,
        mosaic=1.0,
        cache=True
    )

    print("\n" + "="*60)
    print("✅ TRAINING COMPLETE!")
    print("="*60)
    print(f"\n📁 Best model: runs/train/screen_detector_v1/weights/best.pt")
    print(f"📁 Last model: runs/train/screen_detector_v1/weights/last.pt")
    print(f"📊 Results: runs/train/screen_detector_v1/")
    print("\n🎯 Next: Test with live screen detection!")

# This is required for Windows multiprocessing
if __name__ == '__main__':
    train_model()
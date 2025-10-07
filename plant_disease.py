import torch
import torch.nn.functional as F
from torchvision import transforms, models
from PIL import Image
import argparse

# ---------------------------
# Device configuration
# ---------------------------
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---------------------------
# Define preprocessing (should match training transforms)
# ---------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),    # resize to model input size
    transforms.ToTensor(),            # convert to tensor
    transforms.Normalize([0.485, 0.456, 0.406],  # mean (ImageNet)
                         [0.229, 0.224, 0.225]) # std (ImageNet)
])

# ---------------------------
# Load your trained model
# ---------------------------
# Example: If you trained ResNet18
model = models.resnet18(pretrained=False)
num_classes = 38   # change this to your dataset classes
model.fc = torch.nn.Linear(model.fc.in_features, num_classes)

# Load weights
model.load_state_dict(torch.load("plant_disease_model.pth", map_location=DEVICE))
model = model.to(DEVICE)
model.eval()

# ---------------------------
# Define class names (same order as training dataset)
# ---------------------------
class_names = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    # ... add all your dataset classes here ...
    "Tomato___healthy"
]

# ---------------------------
# Prediction function
# ---------------------------
def predict_image(image_path, model, class_names, threshold=0.6):
    model.eval()

    # Load and preprocess image
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        output = model(image)                      # raw logits
        probs = F.softmax(output, dim=1)           # probabilities
        confidence, pred = torch.max(probs, 1)     # top confidence + index
        confidence = confidence.item()
        pred = pred.item()

    # Reject if not confident
    if confidence < threshold:
        return "❌ Please provide a proper leaf photo or this disease is not trained yet."
    else:
        return f"✅ Predicted: {class_names[pred]} (Confidence: {confidence:.2f})"

# ---------------------------
# Main function with CLI
# ---------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plant Disease Prediction")
    parser.add_argument("--image", type=str, required=True, help="Path to the image file")
    args = parser.parse_args()

    result = predict_image(args.image, model, class_names)
    print(result)

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from torchvision import transforms
from PIL import Image
import sys

# -------------------------
# Device
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -------------------------
# PlantVillage 38 classes
class_names = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
    'Blueberry___healthy',
    'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy',
    'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot', 'Peach___healthy',
    'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
    'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch', 'Strawberry___healthy',
    'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight',
    'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy'
]

# -------------------------
# Attention Module (same as training)
class Attention(nn.Module):
    def __init__(self, in_channels):
        super(Attention, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, in_channels // 8, kernel_size=1)
        self.conv2 = nn.Conv2d(in_channels // 8, in_channels, kernel_size=1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        attn = F.adaptive_avg_pool2d(x, 1)  # Global Average Pool
        attn = F.relu(self.conv1(attn))
        attn = self.sigmoid(self.conv2(attn))
        return x * attn

# -------------------------
# ResNet + Attention Model (same as training)
class ResNetAttention(nn.Module):
    def __init__(self, num_classes):
        super(ResNetAttention, self).__init__()
        self.resnet = models.resnet50(weights=None)
        self.resnet.fc = nn.Identity()  # remove classifier
        self.attn = Attention(2048)
        self.fc = nn.Linear(2048, num_classes)

    def forward(self, x):
        x = self.resnet(x)  # feature vector (batch, 2048)
        x = x.unsqueeze(-1).unsqueeze(-1)  # make it 4D for attention
        x = self.attn(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

# -------------------------
# Load trained model
NUM_CLASSES = len(class_names)
MODEL_PATH = r"c:\CEP\agrotech\resnet_attention_plant_disease_all.pth"

model = ResNetAttention(NUM_CLASSES).to(DEVICE)
state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
model.load_state_dict(state_dict)
model.eval()

print("✅ Model loaded successfully!")

# -------------------------
# Image Preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])  # same as training
])

# -------------------------
# Prediction Function
def predict_image(image_path, model, class_names, threshold=0.99):
    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        output = model(image)
        probs = F.softmax(output, dim=1)
        confidence, pred = torch.max(probs, 1)

    confidence = confidence.item()
    pred = pred.item()

    if confidence < threshold:
        return "❌ Please provide a proper leaf photo or this disease is not trained yet."
    else:
        return f"✅ Predicted: {class_names[pred]} (Confidence: {confidence:.2f})"

# -------------------------
# Example"
def predict_disease(image_path):
    return predict_image(image_path, model, class_names)


import io
import os

import mlflow
import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from torchvision import transforms


# MLflow configuration
MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000",
)

MODEL_URI = "models:/food11@champion"


# Food-11 classes
CLASS_NAMES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]


# Same preprocessing used during training
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=IMAGENET_MEAN,
            std=IMAGENET_STD,
        ),
    ]
)


# Connect to MLflow and load the champion model once at startup
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

model = mlflow.pyfunc.load_model(MODEL_URI)


# FastAPI application
app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(file: UploadFile = File(...)):
    # Basic file-type validation
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(
            status_code=400,
            detail="File must be a JPEG or PNG image",
        )

    contents = file.file.read()

    # Decode the uploaded image
    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Could not decode the uploaded image",
        )

    # Apply the same preprocessing as training
    tensor = transform(image).unsqueeze(0)

    # Run inference through the MLflow pyfunc model
    try:
        logits = model.predict(tensor.numpy())
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Model inference failed",
        ) from exc

    # Convert logits to probabilities
    logits_tensor = torch.as_tensor(logits)
    probabilities = torch.softmax(logits_tensor, dim=1)

    confidence, predicted_index = torch.max(
        probabilities,
        dim=1,
    )

    return {
        "category": CLASS_NAMES[predicted_index.item()],
        "confidence": confidence.item(),
    }
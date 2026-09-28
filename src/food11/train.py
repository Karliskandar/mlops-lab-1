import argparse
from pathlib import Path
import mlflow
import mlflow.pytorch

import torch
from torch import nn
from torchvision.models import ResNet18_Weights, resnet18
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

ROOT = Path(__file__).resolve().parents[2]


IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
INPUT_SIZE = (224, 224)


MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
EXPERIMENT_NAME = "food11"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train a ResNet18 model on Food-11"
    )
    parser.add_argument(
        "--dataset",
        choices=["mini", "processed"],
        default="mini",
        help="Dataset to use: mini or processed",
    )
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    return parser.parse_args()


def resolve_dataset_root(dataset: str) -> Path:
    folder = "food11_processed_mini" if dataset == "mini" else "food11_processed"
    dataset_root = ROOT / "local_data" / folder
    if not dataset_root.is_dir():
        raise FileNotFoundError(f"Dataset not found at {dataset_root}")
    return dataset_root


def build_dataloaders(
    dataset_root: Path,
    batch_size: int,
    num_workers: int = 0,
):
    transform = transforms.Compose(
        [
            transforms.Resize(INPUT_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=IMAGENET_MEAN,
                std=IMAGENET_STD,
            ),
        ]
    )

    splits = {}

    for name, folder in (
        ("train", "training"),
        ("val", "validation"),
        ("test", "evaluation"),
    ):
        split_path = dataset_root / folder

        if not split_path.is_dir():
            raise FileNotFoundError(
                f"Missing split folder: {split_path}"
            )

        splits[name] = datasets.ImageFolder(
            split_path,
            transform=transform,
        )

    if not (
        splits["train"].classes
        == splits["val"].classes
        == splits["test"].classes
    ):
        raise ValueError(
            "Class mismatch between splits: "
            f"train={splits['train'].classes}, "
            f"val={splits['val'].classes}, "
            f"test={splits['test'].classes}"
        )

    train_loader = DataLoader(
        splits["train"],
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
    )

    val_loader = DataLoader(
        splits["val"],
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )

    test_loader = DataLoader(
        splits["test"],
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )

    return train_loader, val_loader, test_loader


def build_model(num_classes: int, device: torch.device) -> nn.Module:
    weights = ResNet18_Weights.DEFAULT
    model = resnet18(weights=weights)

    for param in model.parameters():
        param.requires_grad = False

    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)

    model = model.to(device)

    return model

def build_training_components(
    model: nn.Module,
    learning_rate: float,
):
    criterion = nn.CrossEntropyLoss()

    optimizer = torch.optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=learning_rate,
    )

    return criterion, optimizer

def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> float:
    model.train()

    # Keep frozen BatchNorm layers in evaluation mode

    for module in model.modules():
        if isinstance(module, nn.BatchNorm2d):
            module.eval()

    running_loss = 0.0
    total_samples = 0

    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, labels)

        loss.backward()

        optimizer.step()

        batch_size = images.size(0)
        running_loss += loss.item() * batch_size
        total_samples += batch_size

    return running_loss / total_samples


def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, float]:
    model.eval()

    running_loss = 0.0
    correct = 0
    total_samples = 0

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            outputs = model(images)
            loss = criterion(outputs, labels)

            batch_size = images.size(0)
            running_loss += loss.item() * batch_size
            total_samples += batch_size

            predictions = outputs.argmax(dim=1)
            correct += (predictions == labels).sum().item()

    average_loss = running_loss / total_samples
    accuracy = correct / total_samples

    return average_loss, accuracy



def main() -> None:
    args = parse_args()

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    dataset_root = resolve_dataset_root(args.dataset)


    train_loader, val_loader, test_loader = build_dataloaders(
        dataset_root,
        args.batch_size,
    )

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    num_classes = len(train_loader.dataset.classes)

    model = build_model(
        num_classes,
        device,
    )

    criterion, optimizer = build_training_components(
        model,
        args.lr,
    )

    with mlflow.start_run():
        mlflow.log_params(
            {
                "dataset": args.dataset,
                "epochs": args.epochs,
                "lr": args.lr,
                "batch_size": args.batch_size,
                "model": "resnet18",
                "num_classes": num_classes,
                "training_mode":"feature_extraction",
            }
        )

        for epoch in range(args.epochs):
            train_loss = train_one_epoch(
                model,
                train_loader,
                criterion,
                optimizer,
                device,
            )

            val_loss, val_accuracy = evaluate(
                model,
                val_loader,
                criterion,
                device,
            )

            mlflow.log_metric(
                "train_loss",
                train_loss,
                step=epoch,
            )

            mlflow.log_metric(
                "val_loss",
                val_loss,
                step=epoch,
            )

            mlflow.log_metric(
                "val_accuracy",
                val_accuracy,
                step=epoch,
            )

            print(
                f"Epoch {epoch + 1}/{args.epochs} "
                f"- train_loss: {train_loss:.4f} "
                f"- val_loss: {val_loss:.4f} "
                f"- val_accuracy: {val_accuracy:.4f}"
            )

        _, test_accuracy = evaluate(
            model,
            test_loader,
            criterion,
            device,
        )

        mlflow.log_metric(
            "test_accuracy",
            test_accuracy,
        )

        # Save a CPU-portable copy of the trained model
        model.to("cpu")

        mlflow.pytorch.log_model(
            model,
            name="model",
            serialization_format="pickle",
        )

        # Restore the model to the original training device
        model.to(device)

        print(f"Test accuracy: {test_accuracy:.4f}")


    print("Dataset:", args.dataset)
    print("Dataset path:", dataset_root)
    print("Epochs:", args.epochs)
    print("Learning rate:", args.lr)
    print("Batch size:", args.batch_size)

    print("Training images:", len(train_loader.dataset))
    print("Validation images:", len(val_loader.dataset))
    print("Evaluation images:", len(test_loader.dataset))

    print("Device:", device)

    if device.type == "cuda":
        print("GPU:", torch.cuda.get_device_name(0))



    print("Classes:", train_loader.dataset.classes)
    print("Number of classes:", num_classes)
    print("Final model layer:", model.fc)
    print("Model is on", next(model.parameters()).device)

    
if __name__ == "__main__":
    main()
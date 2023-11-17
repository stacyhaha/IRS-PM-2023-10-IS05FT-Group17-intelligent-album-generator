# -*- coding: utf-8 -*-

import torch
import pyheif
from torchvision import models, transforms
from PIL import Image
from pathlib import Path


class BackgroundExtractor:
    def __init__(self, weights_path, map_file_path):
        # Load the pretrained Place365 model using ResNet-50 architecture
        self.class_map = self.create_class_map_from_file(map_file_path)

        self.model = models.resnet50(num_classes=365)

        # Load the weights
        checkpoint = torch.load(weights_path, map_location='cpu')
        state_dict = checkpoint['state_dict']

        # Remove the prefix 'module.' from state_dict keys if present
        state_dict = {k.replace('module.', ''): v for k, v in state_dict.items()}

        self.model.load_state_dict(state_dict)
        self.model.eval()

        # Define the transformations for the images
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])


    def predict(self, Input):
        # Load and preprocess the image
        if Input.lower().endswith("heic"):
            image = self.transfer_heic_file(Input).convert("RGB")
        else:
            image = Image.open(Input).convert("RGB")
        image_tensor = self.transform(image).unsqueeze(0)

        # Detect scene
        with torch.no_grad():
            output = self.model(image_tensor)
            scene_class_index = torch.argmax(output, dim=1).item()

            return self.class_map.get(scene_class_index, "Unknown")
        
    def transfer_heic_file(self, image_path):
        img_path = Path(image_path)
        img_binary = img_path.open("rb").read()
        heif_file = pyheif.read(img_binary)
        img = Image.frombytes(data=heif_file.data, mode=heif_file.mode, size=heif_file.size)
        return img
    


    def create_class_map_from_file(self, filename):
        class_map = {}
        with open(filename, 'r') as f:
            for index, line in enumerate(f):
                # Extract primary category from the class name (e.g., '/r/restaurant_patio' -> 'restaurant')
                class_name = line.strip().split(' ')[0].split('/')[2].split('_')[0]
                class_map[index] = class_name
        return class_map


if __name__ == "__main__":
    # Specify path to the PyTorch model and categories file
    weights_path = r'/Users/stacy/iss/places365-master/resnet50_places365.pth.tar'
    categories_file = r'/Users/stacy/iss/places365-master/categories_places365.txt'

    detector = BackgroundExtractor(weights_path, categories_file)

    # Example detection
    scene = detector.predict(r"/Users/stacy/Downloads/IMG_6194.HEIC")
    print(scene)  # This will print the primary part of the scene name.

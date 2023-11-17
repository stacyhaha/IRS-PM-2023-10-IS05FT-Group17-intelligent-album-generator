# # -*- coding utf-8 -*-
# """
# -------------------------------------------------
#    File Name：     dedup_server.py
#    Author :
#    time：
#    last edit time:
#    Description :   去重服务
# -------------------------------------------------

import os
from PIL import Image
import pyheif
from pathlib import Path
import imagehash

class DedupServer:
    def __init__(self, hash_method=imagehash.average_hash, similarity_threshold=5, target_size=(256, 256)):
        self.hash_method = hash_method
        self.similarity_threshold = similarity_threshold
        self.target_size = target_size

    def calculate_hash(self, image_path):
        if image_path.lower().endswith("heic"):
            image = self.transfer_heic_file(image_path).convert("RGB")
        else:
            image = Image.open(image_path).convert("RGB")

        resized_image = image.resize(self.target_size)
        return str(self.hash_method(resized_image))  # Convert hash to string

    def find_similar_images(self, inputs):
        hashes = {}
        similar_pairs = []

        for filename in inputs:
            file_path = filename

            try:
                hash_value = self.calculate_hash(file_path)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue

            for existing_hash, existing_path in hashes.items():
                if hash_value == existing_hash or int(hash_value, 16) - int(existing_hash, 16) < self.similarity_threshold:
                    # Check if the pair is not already in similar_pairs
                    if (existing_path, file_path) not in similar_pairs and (file_path, existing_path) not in similar_pairs:
                        similarity_score = self.calculate_similarity_score(hash_value, existing_hash)
                        if similarity_score >= self.similarity_threshold:
                            similar_pairs.append((existing_path, file_path))

            hashes[hash_value] = file_path

        return similar_pairs

    def calculate_similarity_score(self, hash1, hash2):
        max_hash_difference = 64.0  # Assuming 64 is the maximum hash difference
        hash_difference = int(hash1, 16) - int(hash2, 16)
        similarity_score = max(0, 1 - abs(hash_difference) / max_hash_difference)
        return similarity_score * 100  # Convert to percentage

    def predict(self, inputs, **kwargs):
        similar_pairs = self.find_similar_images(inputs)

        selected_images = set()
        excluded_images = set()

        # print("Selected Images:")
        for pair in similar_pairs:
            similarity_score = self.calculate_similarity_score(self.calculate_hash(pair[0]), self.calculate_hash(pair[1]))
            print(f"Similar Pair (Similarity: {similarity_score:.2f}%):")
            print(f"  Selected Image: {pair[0]}")
            selected_images.add(pair[0])
            excluded_images.add(pair[1])
            print(f"  Excluded Image: {pair[1]}")
            print()

        # Include any remaining images that were not part of a similar pair
        all_images = set([image_path for pair in similar_pairs for image_path in pair[:2]])
        remaining_images = set(inputs) - all_images

        print("Remaining Images:")
        for image in remaining_images:
            print(f"  {image}")
            excluded_images.add(image)

        combined_images = selected_images | remaining_images  # Combine selected_images and remaining_images
        return combined_images, excluded_images
    
    def transfer_heic_file(self, image_path):
        img_path = Path(image_path)
        img_binary = img_path.open("rb").read()
        heif_file = pyheif.read(img_binary)
        img = Image.frombytes(data=heif_file.data, mode=heif_file.mode, size=heif_file.size)
        return img

# Example usage
if __name__ == "__main__":
    dedup_server = DedupServer(similarity_threshold=40)
    input_images = [
        "/Users/stacy/Downloads/IMG_6193.HEIC",
        "/Users/stacy/Downloads/IMG_6189.HEIC",
        "/Users/stacy/Downloads/IMG_6188.HEIC",
        "/Users/stacy/Downloads/IMG_6188_副本.HEIC"
    ]
    combined_images, excluded_images = dedup_server.predict(input_images)

    print("\nSummary:")
    # print(f"Combined Images (Selected + Remaining): {combined_images}")
    print(f"Unique Images: {excluded_images}")









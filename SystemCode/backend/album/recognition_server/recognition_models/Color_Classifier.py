import numpy as np
import os
import cv2
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model
from sklearn.metrics import classification_report


# Constants
DATADIR = r'C:\Users\nn010\Desktop\smart_album_generator-main\archive\ColorClassification'
CATEGORIES = ['orange', 'Violet', 'red', 'Blue', 'Green', 'Black', 'Brown', 'White']
IMG_SIZE = 100
MODEL_PATH = r"C:\Users\nn010\Desktop\smart_album_generator-main\album\recognition_server\recognition_models\color_classifier_model.h5"


def display_all_categories():
    cols = 2
    rows = 4
    col_index = 0
    row_index = 0
    f, axarr = plt.subplots(rows, cols, figsize=(12, 12))

    for category in CATEGORIES:
        path = os.path.join(DATADIR, category)
        for img in os.listdir(path):
            img_array = cv2.imread(os.path.join(path, img), cv2.COLOR_BGR2RGB)
            axarr[row_index, col_index].imshow(img_array)
            axarr[row_index, col_index].set_title(category)
            break
        col_index += 1
        if col_index == cols:
            row_index += 1
            col_index = 0
    plt.show()


def create_training_data():
    training_data = []
    for category in CATEGORIES:
        path = os.path.join(DATADIR, category)
        class_num = CATEGORIES.index(category)
        for img in os.listdir(path):
            try:
                img_array = cv2.imread(os.path.join(path, img))
                new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
                training_data.append([new_array, class_num])
            except Exception as e:
                pass
    return training_data


def main():
    # Load and preprocess data
    training_data = create_training_data()
    lenofimage = len(training_data)
    X = []
    y = []

    for categories, label in training_data:
        X.append(categories)
        y.append(label)

    X = np.array(X).reshape(-1, IMG_SIZE, IMG_SIZE, 3) / 255.0
    y = np.array(y)

    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    # Data augmentation
    datagen = ImageDataGenerator(rotation_range=20,
                                 width_shift_range=0.2,
                                 height_shift_range=0.2,
                                 shear_range=0.2,
                                 zoom_range=0.2,
                                 horizontal_flip=True,
                                 fill_mode='nearest')
    datagen.fit(X_train)

    # Build and compile the CNN model
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 3)),
        MaxPooling2D(2, 2),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(len(CATEGORIES), activation='softmax')
    ])

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # Train the model using data augmentation
    model.fit(datagen.flow(X_train, y_train, batch_size=32), epochs=10, validation_data=(X_test, y_test))

    model.save(MODEL_PATH)  # Updated
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred, axis=1)

    # Classification report
    print("Classification Report:\n", classification_report(y_test, y_pred_classes, target_names=CATEGORIES))


def Main_color_Extractor(image_path, model_path=MODEL_PATH):  # Updated
    model = load_model(model_path)

    # Load and preprocess the image
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = np.array(img).reshape(-1, IMG_SIZE, IMG_SIZE, 3) / 255.0

    # Get predictions
    predictions = model.predict(img)
    predicted_class = np.argmax(predictions, axis=1)[0]

    return CATEGORIES[predicted_class]

if __name__ == "__main__":
    #main()
    image_path = r"C:\Users\nn010\Desktop\pic.jpg"
    Main_color = Main_color_Extractor(image_path)
    print(f"Predicted color category for the image is: {Main_color}")
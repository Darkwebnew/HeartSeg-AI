"""
train.py
HeartSeg AI v2 — Cardiac MRI Classification

Dataset Structure:
dataset/
 ├── Normal/
 └── Sick/

Run:
python train.py

Optional:
python train.py --epochs 20 --batch_size 4
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_GPU_ALLOCATOR'] = 'cuda_malloc_async'

import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.utils import class_weight

from tensorflow.keras import layers, Model, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import (
    ModelCheckpoint,
    EarlyStopping,
    ReduceLROnPlateau
)

# =========================================================
# GPU MEMORY SETTINGS
# =========================================================

gpus = tf.config.experimental.list_physical_devices('GPU')

if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)

        print("\nGPU Memory Growth Enabled")

    except RuntimeError as e:
        print(e)

# =========================================================
# CONFIG
# =========================================================

DATASET_PATH = "dataset"

IMG_SIZE = 96
BATCH_SIZE = 4
EPOCHS = 20

MODEL_DIR = "h5"
OUTPUT_DIR = "outputs"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "heart_model.h5")

# =========================================================
# LOAD DATASET PATHS
# =========================================================

image_paths = []
labels = []

classes = ["Normal", "Sick"]

print("\n================================================")
print("HeartSeg AI v2")
print(f"TensorFlow: {tf.__version__}")
print(f"GPUs: {len(gpus)}")
print("================================================")

print("\n================================================")
print("Loading Dataset")
print("================================================")

for class_index, class_name in enumerate(classes):

    class_dir = os.path.join(DATASET_PATH, class_name)

    print(f"\nScanning {class_name}...")

    count = 0

    for root, dirs, files in os.walk(class_dir):

        for file in files:

            if file.lower().endswith((".png", ".jpg", ".jpeg")):

                full_path = os.path.join(root, file)

                image_paths.append(full_path)
                labels.append(class_index)

                count += 1

    print(f"Loaded {count} images")

labels = np.array(labels)

print(f"\nTotal Images Loaded: {len(image_paths)}")

# =========================================================
# SPLIT DATASET
# =========================================================

train_paths, val_paths, train_labels, val_labels = train_test_split(
    image_paths,
    labels,
    test_size=0.2,
    random_state=42,
    stratify=labels
)

print(f"\nTrain Samples: {len(train_paths)}")
print(f"Validation Samples: {len(val_paths)}")

# =========================================================
# CLASS WEIGHTS
# =========================================================

cw = class_weight.compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_labels),
    y=train_labels
)

class_weights = dict(enumerate(cw))

print("\nClass Weights:")
print(class_weights)

# =========================================================
# DATA GENERATOR
# =========================================================

def data_generator(paths, labels, batch_size):

    while True:

        indices = np.arange(len(paths))
        np.random.shuffle(indices)

        for start in range(0, len(paths), batch_size):

            batch_indices = indices[start:start + batch_size]

            batch_images = []
            batch_labels = []

            for idx in batch_indices:

                img = cv2.imread(paths[idx], cv2.IMREAD_GRAYSCALE)

                if img is None:
                    continue

                img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
                img = img.astype(np.float32) / 255.0

                batch_images.append(img[..., np.newaxis])
                batch_labels.append(labels[idx])

            yield np.array(batch_images), np.array(batch_labels)

# =========================================================
# MODEL
# =========================================================

def build_model():

    inputs = Input(shape=(IMG_SIZE, IMG_SIZE, 1))

    x = layers.Conv2D(16, 3, activation='relu', padding='same')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D()(x)

    x = layers.Conv2D(32, 3, activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D()(x)

    x = layers.Conv2D(64, 3, activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D()(x)

    x = layers.Conv2D(128, 3, activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)

    x = layers.GlobalAveragePooling2D()(x)

    x = layers.Dense(64, activation='relu')(x)
    x = layers.Dropout(0.4)(x)

    outputs = layers.Dense(2, activation='softmax')(x)

    model = Model(inputs, outputs)

    return model

model = build_model()

model.compile(
    optimizer=Adam(1e-4),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# =========================================================
# CALLBACKS
# =========================================================

callbacks = [

    ModelCheckpoint(
        MODEL_PATH,
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),

    EarlyStopping(
        patience=4,
        restore_best_weights=True,
        verbose=1
    ),

    ReduceLROnPlateau(
        factor=0.5,
        patience=2,
        verbose=1
    )
]

# =========================================================
# TRAINING
# =========================================================

print("\n================================================")
print("Training Started")
print("================================================")

train_gen = data_generator(
    train_paths,
    train_labels,
    BATCH_SIZE
)

val_gen = data_generator(
    val_paths,
    val_labels,
    BATCH_SIZE
)

history = model.fit(

    train_gen,

    steps_per_epoch=len(train_paths) // BATCH_SIZE,

    validation_data=val_gen,

    validation_steps=len(val_paths) // BATCH_SIZE,

    epochs=EPOCHS,

    class_weight=class_weights,

    callbacks=callbacks,

    verbose=1
)

# =========================================================
# SAVE ACCURACY GRAPH
# =========================================================

plt.figure(figsize=(10, 5))

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])

plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')

plt.legend(['Train', 'Validation'])

plt.savefig(os.path.join(OUTPUT_DIR, 'accuracy.png'))

plt.close()

# =========================================================
# SAVE LOSS GRAPH
# =========================================================

plt.figure(figsize=(10, 5))

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])

plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')

plt.legend(['Train', 'Validation'])

plt.savefig(os.path.join(OUTPUT_DIR, 'loss.png'))

plt.close()

# =========================================================
# PREDICTIONS
# =========================================================

print("\n================================================")
print("Evaluating Model")
print("================================================")

y_true = []
y_pred = []

for i in range(min(1000, len(val_paths))):

    img = cv2.imread(val_paths[i], cv2.IMREAD_GRAYSCALE)

    if img is None:
        continue

    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = img.astype(np.float32) / 255.0

    pred = model.predict(
        np.expand_dims(img[..., np.newaxis], axis=0),
        verbose=0
    )

    pred_class = np.argmax(pred)

    y_true.append(val_labels[i])
    y_pred.append(pred_class)

print("\nClassification Report:\n")

print(classification_report(
    y_true,
    y_pred,
    target_names=classes
))

# =========================================================
# CONFUSION MATRIX
# =========================================================

cm = confusion_matrix(y_true, y_pred)

plt.figure(figsize=(6, 6))

plt.imshow(cm)

plt.title("Confusion Matrix")

plt.colorbar()

plt.xticks([0,1], classes)
plt.yticks([0,1], classes)

plt.xlabel("Predicted")
plt.ylabel("Actual")

for i in range(2):
    for j in range(2):
        plt.text(j, i, cm[i, j], ha='center', va='center')

plt.savefig(os.path.join(OUTPUT_DIR, 'confusion_matrix.png'))

plt.close()

# =========================================================
# SAMPLE OUTPUTS
# =========================================================

sample_dir = os.path.join(OUTPUT_DIR, "samples")
os.makedirs(sample_dir, exist_ok=True)

for i in range(10):

    img = cv2.imread(val_paths[i], cv2.IMREAD_GRAYSCALE)

    if img is None:
        continue

    img_resized = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img_norm = img_resized.astype(np.float32) / 255.0

    pred = model.predict(
        np.expand_dims(img_norm[..., np.newaxis], axis=0),
        verbose=0
    )

    pred_class = classes[np.argmax(pred)]
    true_class = classes[val_labels[i]]

    plt.figure(figsize=(4,4))

    plt.imshow(img_resized, cmap='gray')

    plt.title(f"True: {true_class}\nPred: {pred_class}")

    plt.axis('off')

    plt.savefig(
        os.path.join(sample_dir, f"sample_{i}.png")
    )

    plt.close()

# =========================================================
# DONE
# =========================================================

print("\n================================================")
print("TRAINING COMPLETE")
print("================================================")

print(f"\nModel Saved: {MODEL_PATH}")

print("\nGenerated Outputs:")
print("outputs/")
print(" ├── accuracy.png")
print(" ├── loss.png")
print(" ├── confusion_matrix.png")
print(" └── samples/")
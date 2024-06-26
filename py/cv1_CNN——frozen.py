# -*- coding: utf-8 -*-
"""CMT316_Session_CV1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1SX4o9_jmIC2QghxaP95z3ut50gILCIQR

**Convolutional Neural Networks**

CNN-related demos
"""

# We use Fashion MNIST dataset, which is provided by Keras
# The following is the code to load data etc. same as last session

# import Keras & Tensorflow
import tensorflow as tf
import keras

# Load image data
fashion_mnist = keras.datasets.fashion_mnist
(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()
class_names = ["T-shirt/top", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"]

# Data preparation:
#   Map intensities from [0--255] to 0.0--1.0
x_train = x_train / 255.0
x_test = x_test / 255.0

"""**Basic Convolutional Neural Network Example**"""

early_stopping_cb = keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True)
model = keras.models.Sequential([
    keras.layers.Conv2D(64, 7, activation="relu", padding="same",
                        input_shape=[28, 28, 1]),
    keras.layers.MaxPooling2D(2),
    keras.layers.Conv2D(128, 3, activation="relu", padding="same"),
    keras.layers.Conv2D(128, 3, activation="relu", padding="same"),
    keras.layers.MaxPooling2D(2),
    keras.layers.Conv2D(256, 3, activation="relu", padding="same"),
    keras.layers.Conv2D(256, 3, activation="relu", padding="same"),
    keras.layers.MaxPooling2D(2),
    keras.layers.Flatten(),
    keras.layers.Dense(128, activation="relu"),
    keras.layers.Dropout(0.5),
    keras.layers.Dense(64, activation="relu"),
    keras.layers.Dropout(0.5),
    keras.layers.Dense(10, activation="softmax")
])
model.compile(loss = "sparse_categorical_crossentropy", optimizer="sgd", metrics = ["accuracy"])
# reshape: map data to 4D, with the last dimension of 1 channel (grayscale)
history = model.fit(x_train.reshape((x_train.shape[0], 28, 28, 1)), y_train, epochs = 60, validation_split=0.1, callbacks=[early_stopping_cb])
model.evaluate(x_test.reshape(x_test.shape[0], 28, 28, 1), y_test)

"""**Classification using Pre-trained Networks**"""

# import Keras & Tensorflow
import tensorflow as tf
import keras

# Load pre-trained Resnet50
model = keras.applications.resnet50.ResNet50(weights="imagenet")



# Connect with Google Drive
from google.colab import drive
drive.mount('/content/gdrive')

model.summary()

# Load in image and perform classification
import keras.utils as image
# import keras.preprocessing.image as image # earlier version of Tensorflow uses this
img = image.load_img("/content/gdrive/My Drive/IndianElephant.jpg", target_size=(224, 224)) # the image is in the root of Google Drive, you can replace it with an arbitrary image you have
# convert the image pixels to a numpy array
img = image.img_to_array(img)
# reshape data for the model
img = img.reshape((1, img.shape[0], img.shape[1], img.shape[2]))
# prepare the image for the model
img = keras.applications.resnet50.preprocess_input(img)
Y_prob = model.predict(img)
# Show top K prediction
top_K = keras.applications.resnet50.decode_predictions(Y_prob, top=3)
for class_id, name, y_proba in top_K[0]:
  print("class_id:", class_id, "name:", name, " ", y_proba*100, "%")

"""**Fine-tuning pre-trained models**"""

# We use Tensorflow provided tf_flowers dataset
# https://www.tensorflow.org/tutorials/load_data/images
import tensorflow_datasets as tfds
dataset, info = tfds.load("tf_flowers", as_supervised=True, with_info=True)
dataset_size = info.splits["train"].num_examples
print("size: ", dataset_size)
class_names = info.features["label"].names
print("classes: ", class_names)
n_classes = info.features["label"].num_classes
print("num. classes: ", n_classes)

# Split data into training, test and validation
# Setting as_supervised to True to include ground truth labels
test_set = tfds.load("tf_flowers", split="train[:10%]", as_supervised=True)
valid_set = tfds.load("tf_flowers", split="train[10%:25%]", as_supervised=True)
train_set = tfds.load("tf_flowers", split="train[25%:]", as_supervised=True)

# Data preprocessing
def preprocess(image, label):
  resized_image = tf.image.resize(image, [224, 224])
  final_image = keras.applications.xception.preprocess_input(resized_image)
  return final_image, label

batch_size = 32
train_set = train_set.shuffle(1000)
train_set = train_set.map(preprocess).repeat().batch(batch_size).prefetch(1)
valid_set = valid_set.map(preprocess).repeat().batch(batch_size).prefetch(1)
test_set = test_set.map(preprocess).batch(batch_size).prefetch(1)

# Fine-tuning xception model
base_model = keras.applications.xception.Xception(weights="imagenet", include_top=False)
avg = keras.layers.GlobalAveragePooling2D()(base_model.output)
output = keras.layers.Dense(n_classes, activation="softmax")(avg)
model = keras.Model(inputs=base_model.input, outputs=output)
model.summary()

# Training with existing layers fixed
lr_schedule = keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate=0.02,
    decay_steps=10000,
    decay_rate=0.9)
for layer in base_model.layers:
  layer.trainable = False
optimizer = keras.optimizers.SGD(learning_rate=lr_schedule, momentum=0.9)
model.compile(loss="sparse_categorical_crossentropy", optimizer=optimizer, metrics=["accuracy"])
history = model.fit(train_set, epochs=5, steps_per_epoch=dataset_size*0.75//batch_size, validation_data=valid_set, validation_steps = dataset_size*0.15//batch_size)

# The model can be further trained with base layers unfrozen
for layer in base_model.layers:
  layer.trainable = True

optimizer = keras.optimizers.SGD(learning_rate=lr_schedule, momentum=0.9)
model.compile(loss="sparse_categorical_crossentropy", optimizer=optimizer, metrics=["accuracy"])
history = model.fit(train_set, epochs=5, steps_per_epoch=dataset_size*0.75//batch_size, validation_data=valid_set, validation_steps = dataset_size*0.15//batch_size)
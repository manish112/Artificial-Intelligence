import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import RMSprop
import numpy as np
from keras.preprocessing import image
import cv2

import matplotlib.pyplot as plt
import os


class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('acc')>0.90):
      print("\nReached 90.0% accuracy so cancelling training!")
      self.model.stop_training = True


callbacks = myCallback()
# All images will be rescaled by 1./255
train_datagen = ImageDataGenerator(rescale=1/255)
validation_datagen = ImageDataGenerator(rescale=1/255)

dataPath="D://MS//BITSPilani//Sem4//project//main//ui//data//"


train_generator = train_datagen.flow_from_directory(
        dataPath+'training',  
        target_size=(300, 300),  
        color_mode='grayscale',
		shuffle=False,
		batch_size=4,
		class_mode='categorical')
		
		
validation_generator = validation_datagen.flow_from_directory(
        dataPath+'validation',  
        target_size=(300, 300),  
        color_mode='grayscale',
		shuffle=False,
		batch_size=4,
		class_mode='categorical')
		
label_map = (train_generator.class_indices)
np.save(dataPath+'model//class_labels', train_generator.class_indices)

#(x_train, y_train)= (train_generator.class_indices)

print(label_map)

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(16, (3,3), activation='relu', input_shape=(300, 300, 1)),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(16, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(train_generator.num_classes, activation='softmax')
])

print("Number of classes: "+str(train_generator.num_classes))


model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])
model.summary()

		
history = model.fit_generator(
      train_generator,
      steps_per_epoch=28,  
      epochs=15,
	  validation_data = validation_generator,
      validation_steps=28,
	  callbacks=[callbacks])
	  
#path = "D://MS//BITSPilani//Sem4//project//main//ui//data//test/1.bmp"
##img = image.load_img(path, target_size=(150, 150), color_mode="grayscale")
#x = image.img_to_array(img)
#x = np.expand_dims(x, axis=0)
#images = np.vstack([x])
#classes1 = model.predict(images, batch_size=10)
#print(classes1)

tf.keras.models.save_model(model,"D://MS//BITSPilani//Sem4//project//main//ui//data//model/myModel.h5", overwrite=True, include_optimizer=True)
print("Trained model saved")
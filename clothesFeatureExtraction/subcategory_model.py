import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing import image
from tensorflow.keras.utils import plot_model
from sklearn.preprocessing import LabelEncoder
from clothesFeatureExtraction.utils import (
    BODYWEAR,
    BOTTOMWEAR,
    DATA_PATH,
    EPOCHS_SUBCATEGORY,
    FOOTWEAR,
    IMG_HEIGHT,
    IMG_WIDTH,
    MODELS_FILENAME,
    STEPS_PER_EPOCH_SUBCATEGORY,
    SUBCATEGORY,
    TOPWEAR,
    Model,
)

prediction_to_subcategory = {
    0: TOPWEAR,
    1: BOTTOMWEAR,
    2: FOOTWEAR,
    3: BODYWEAR,
}

class SubcategoryModel(Model):
    def __init__(self):
        self.model = self.load_or_train_model(MODELS_FILENAME[SUBCATEGORY])

    def train_model(self, model, train, val, epochs=EPOCHS_SUBCATEGORY, steps_per_epoch=STEPS_PER_EPOCH_SUBCATEGORY, model_name=SUBCATEGORY):
        return super().train_model(model, train, val, epochs, steps_per_epoch, model_name)

    def get_model_prediction(self, data) -> str:
        print("get model prediction - subcategory")
        # print(f"classes: {self.le_category.classes_}")
        print(f"self.model.predict(data) {self.model.predict(data)}")
        print(f"np.argmax(self.model.predict(data)) {np.argmax(self.model.predict(data))}")
        return prediction_to_subcategory[np.argmax(self.model.predict(data))]
    
    def build_model(self, print_summary=False):
        res50 = keras.applications.ResNet50(weights='imagenet', include_top=False, input_shape=(IMG_HEIGHT, IMG_WIDTH, 3))
        res50.trainable=False
        inputs = keras.Input(shape=(IMG_HEIGHT, IMG_WIDTH, 3), name="images")
        x = res50(inputs, training=False)
        x = layers.Conv2D(32, (2, 2), activation='relu')(x)
        x = layers.Flatten()(x)
        x = layers.Dense(1024, activation='relu')(x)
        
        subcategory_branch = self.make_branch(x, len(self.le_category.classes_), 'softmax', 'subCategory')
        # model = keras.Sequential([
        #        res50(inputs, training=False),
        #        layers.Conv2D(32, (2, 2), activation='relu'),
        #        layers.Flatten(),
        #        layers.Dense(1024, activation='relu'),
        #        layers.Dense(512, activation="relu"),
        #        layers.Dense(256, activation='relu'),
        #        layers.Dense(128, activation='relu'),
        #        layers.Dense(64, activation='relu'),
        #        layers.Dense(classes),
        #        layers.Activation('softmax', name='subCategory')
        # ])
        model = keras.Model(inputs=inputs, outputs=[subcategory_branch])
        
        if print_summary:
            model.summary()
            plot_model(model)

        return model
        
    def get_dataframe(self, path=DATA_PATH, filter_subcategory=None, label_encoded_columns=["subCategory"]):
        df, self.le_category = super().get_dataframe(
            path=path,
            filter_subcategory=filter_subcategory,
            label_encoded_columns=label_encoded_columns
        )
        print(f"classes: {self.le_category.classes_}")
        return df
    
    def get_input_array(self, df):
        return super().get_input_array(df, {"subCategory" : df[["subCategory"]]})
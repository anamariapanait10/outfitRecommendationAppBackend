import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing import image
from tensorflow.keras.utils import plot_model
from clothesFeatureExtraction.utils import (
    BODYWEAR,
    DATA_PATH,
    EPOCHS_BODYWEAR,
    IMG_HEIGHT,
    IMG_WIDTH,
    MODELS_FILENAME,
    STEPS_PER_EPOCH_BODYWEAR,
    Model,
)

prediction_to_response = {
    "article_type": {
        0: 'Casual Shoes',
        1: 'Flats',
        2: 'Flip Flops',
        3: 'Formal Shoes',
        4: 'Heels',
        5: 'Sandals',
        6: 'Sports Sandals',
        7:'Sports Shoes',
    },
    "gender": {
        0: "Boys",
        1: "Girls",
        2: "Men",
        3: "Unisex",
        4: "Women",
    },
    "color": {
        0: 'Beige',
        1: "Black",
        2: "Blue",
        3: "Brown",
        4: "Burgundy",
        5: "Charcoal",
        6: "Coffee Brown",
        7: 'Cream',
        8: 'Fluorescent Green',
        9: 'Gold',
        10: 'Green',
        11: 'Grey',
        12: 'Grey Melange',
        13: 'Khaki',
        14: 'Lavender',
        15: 'Lime Green',
        16: 'Magenta',
        17: 'Maroon',
        18: 'Mauve',
        19: 'Multi',
        20: 'Mushroom Brown',
        21: 'Mustard',
        22: 'Navy Blue',
        23: 'Nude',
        24: 'Off White',
        25: 'Olive',
        26: 'Orange',
        27: 'Peach',
        28: 'Pink',
        29: 'Purple',
        30: 'Red',
        31: 'Rust',
        32: 'Sea Green',
        33: 'Silver',
        34: 'Tan',
        35: 'Teal',
        36: 'Turquoise Blue',
        37: 'White',
        38: 'Yellow',
    },
    "season": {
        0: "Fall",
        1: "Spring",
        2: "Summer",
        3: "Winter",
    },
    "usage": {
        0: "Casual",
        1: "Ethnic",
        2: "Formal",
        3: "Party",
        4: "Smart Casual",
        5: "Sports",
    },
}

class BodywearModel(Model):
    def __init__(self):
        self.model = self.load_or_train_model(MODELS_FILENAME[BODYWEAR])
    
    def train_model(self, model, train, val, epochs=EPOCHS_BODYWEAR, steps_per_epoch=STEPS_PER_EPOCH_BODYWEAR, model_name=BODYWEAR):
        return super().train_model(model, train, val, epochs, steps_per_epoch, model_name)

    def get_model_prediction(self, data) -> str:
        predictions = self.model.predict(data)
        print("get model prediction - bodywear")

        result = [
            prediction_to_response[column][np.argmax(predictions[idx][0])]
            for idx, column in enumerate(["article_type", "gender", "color", "season", "usage"])
        ]
        return result
    
    def build_model(self, print_summary=False):
        res50 = keras.applications.ResNet50(weights="imagenet", include_top=False, input_shape=(IMG_HEIGHT, IMG_WIDTH, 3))
        res50.trainable=False
        inputs = keras.Input(shape=(IMG_HEIGHT, IMG_WIDTH, 3), name="images")
        x = res50(inputs, training=False)
        # x = layers.Conv2D(32, (2, 2), activation="relu")(x)
        x = layers.Flatten()(x)
        x = layers.Dense(1024, activation="relu")(x)
    
        # model = keras.Sequential([
        #        res50(inputs, training=False),
        #        layers.Conv2D(32, (2, 2), activation="relu"),
        #        layers.Flatten(),
        #        layers.Dense(1024, activation="relu"),
        #        layers.Dense(512, activation="relu"),
        #        layers.Dense(256, activation="relu"),
        #        layers.Dense(128, activation="relu"),
        #        layers.Dense(64, activation="relu"),
        #        layers.Dense(classes),
        #        layers.Activation("softmax", name="subCategory")
        # ])
        art_type_branch = self.make_branch(x, len(self.le_art_type.classes_), "softmax", "articleType")
        gender_branch = self.make_branch(x, len(self.le_gender.classes_), "softmax", "gender")
        color_branch = self.make_branch(x, len(self.le_color.classes_), "softmax", "baseColour")
        season_branch = self.make_branch(x, len(self.le_season.classes_), "softmax", "season")
        usage_branch = self.make_branch(x, len(self.le_usage.classes_), "softmax", "usage")
        
        model = keras.Model(
            inputs=inputs,
            outputs=[
                art_type_branch, gender_branch, color_branch, season_branch, usage_branch
            ]
        )
        
        if print_summary:
            model.summary()
            plot_model(model)

        return model
    
    def get_dataframe(
        self,
        path=DATA_PATH,
        filter_subcategory=BODYWEAR,
        label_encoded_columns=["articleType", "gender", "baseColour", "season", "usage"],
    ):
        (
            df,
            self.le_art_type,
            self.le_gender,
            self.le_color,
            self.le_season,
            self.le_usage
        ) = super().get_dataframe(
            path=path,
            filter_subcategory=filter_subcategory,
            label_encoded_columns=label_encoded_columns
        )
        print("-"*40)
        print("Label encoders - bodywear model")
        print("articleType", self.le_art_type.classes_)
        print("gender", self.le_gender.classes_)
        print("baseColour", self.le_color.classes_)
        print("season", self.le_season.classes_)
        print("usage", self.le_usage.classes_)
        print("-"*40)
        return df
    
    def get_input_array(self, df):
        return super().get_input_array(
            df,
            { 
                "articleType" : df[["articleType"]],
                "gender" : df[["gender"]],
                "baseColour" : df[["baseColour"]],
                "season" : df[["season"]],
                "usage" : df[["usage"]]
            }
        )
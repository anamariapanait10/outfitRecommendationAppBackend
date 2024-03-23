import numpy as np
import cv2
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing import image
from sklearn.preprocessing import LabelEncoder

LOCAL_PATH = r"C:\Users\Ana\Desktop\Licenta\featureExtraction"
IMAGES_PATH = LOCAL_PATH + "\images"
DATA_PATH = LOCAL_PATH + "\styles.csv"

SUBCATEGORY = "SUBCATEGORY"
TOPWEAR = "TOPWEAR"
BOTTOMWEAR = "BOTTOMWEAR"
FOOTWEAR = "FOOTWEAR"
BODYWEAR = "BODYWEAR"

MODELS_FILENAME = {
    SUBCATEGORY: "subcategory_model",
    TOPWEAR: "topwear_model",
    BOTTOMWEAR: "bottomwear_model", 
    FOOTWEAR: "footwear_model",
    BODYWEAR: "bodywear_model"
}

TRAIN_SIZE = 0.6
VAL_SIZE = 0.2
IMG_WIDTH = 60
IMG_HEIGHT = 80

BATCH_SIZE = 2
EPOCHS_SUBCATEGORY = 5
EPOCHS_TOPWEAR = 10
EPOCHS_BOTTOMWEAR = 15
EPOCHS_FOOTWEAR = 5
EPOCHS_BODYWEAR = 5
STEPS_PER_EPOCH_SUBCATEGORY = 2000
STEPS_PER_EPOCH_TOPWEAR = 500
STEPS_PER_EPOCH_BOTTOMWEAR = 50
STEPS_PER_EPOCH_FOOTWEAR = 2000
STEPS_PER_EPOCH_BODYWEAR = 2000


class Model:
    def __init__(self):
        pass
    
    def get_model_prediction(self, data):
        pass
    
    def train_model(self, model, train, val, epochs, steps_per_epoch, model_name):
        model.compile(optimizer="adam", loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), metrics=["accuracy"])
        model.fit(train, epochs=epochs, steps_per_epoch=steps_per_epoch, validation_data=val)
        model.save(f"models/{MODELS_FILENAME[model_name]}")
        return model
    
    def evaluate_model(self, model, test_data):
        model.evaluate(test_data)
    
    def load_or_train_model(self, model_filename):
        if model_filename not in MODELS_FILENAME.values():
            raise Exception("Invalid model name")
    
        # if the model is already trained, load it
        # else, train it and save it
        print(tf.io.gfile.exists(LOCAL_PATH + rf"\models\{model_filename}"))
        if tf.io.gfile.exists(LOCAL_PATH + rf"\models\{model_filename}"):
            print("Load model...")
            model = keras.models.load_model(LOCAL_PATH + rf"\models\{model_filename}")
        else:
            print("Train model...")
            df = self.get_dataframe()
            print('-'*40)
            print(df.head())
            training_data, validation_data, sub_test = self.get_input_xx(self.get_input_array(df))
            model = self.build_model()
            model = self.train_model(model, training_data, validation_data)
        return model
    
    def get_dataframe(self, path=DATA_PATH, filter_subcategory=None, label_encoded_columns=None):
        print("Read data...")
        df = pd.read_csv(path, on_bad_lines='skip')
        # Keep only Apparel, Footwear and Accessories
        df = df[(df.masterCategory=='Apparel') | (df.masterCategory=='Footwear') | (df.masterCategory=='Accessories')]
        # Drop useless columns and rows
        for column in ["productDisplayName","year"]:
            df = df.drop(column, axis=1)
        for subCategory in ["Innerwear","Apparel Set","Dress","Loungewear and Nightwear","Saree","Socks"]:
            df = df.drop(df[df["subCategory"] == subCategory].index)
        # Drop invalid rows
        df = df.drop(df[(df["articleType"] == "Belts") & (df["subCategory"] == "Topwear")].index)
        df = df.drop(df[(df["articleType"] == "Dresses") & (df["subCategory"] == "Topwear")].index)
        df = df.dropna()
        # Group them into one category
        df["subCategory"] = df["subCategory"].transform(lambda x: "Footwear" if(x in ["Shoes","Flip Flops","Sandal"]) else x)
        print("subCategory: ", df["subCategory"].unique())
        print("-"*40)
        print("art type before: ", df["articleType"].unique())
        if filter_subcategory:
            df = df[df["subCategory"] == filter_subcategory.capitalize()]
        print("subCategory: ", df["subCategory"].unique())
        if label_encoded_columns:
            return self.get_label_encoded_df(df, label_encoded_columns)

        return df

    def get_input_array(self, df, output_dict):
        train_images = np.zeros((len(df.id), IMG_HEIGHT, IMG_WIDTH, 3))
        for row in range(len(df.id)): 
            img_id = df.id.iloc[row]
            img = cv2.imread(IMAGES_PATH + rf"\{img_id}.jpg")
            if img is not None:
                if img.shape != (IMG_HEIGHT, IMG_WIDTH, 3):
                    print(f"Resizing image...with id {img_id}")
                    img = image.load_img(IMAGES_PATH + rf"\{img_id}.jpg", target_size=(IMG_HEIGHT, IMG_WIDTH, 3))

                train_images[row] = img
            
        data = tf.data.Dataset.from_tensor_slices(
            (
                {"images" : train_images},
                output_dict
            )
        )
        print('='*40)
        print(data)

        return data

    def get_input_xx(self, x_input, batch_size = BATCH_SIZE):
        x_input = x_input.shuffle(buffer_size = len(x_input))

        x_train_size = int(TRAIN_SIZE * len(x_input))
        x_val_size = int(VAL_SIZE * len(x_input))

        x_train = x_input.take(x_train_size).batch(batch_size)
        x_val = x_input.skip(x_train_size).take(x_val_size).batch(batch_size)
        x_test = x_input.skip(x_train_size + x_val_size).batch(batch_size)

        return x_train, x_val, x_test
    
    def get_label_encoded_df(self, df, columns):
        les = []
        print("df subcategory: ", df["subCategory"].unique())
        print("df art type: ", df["articleType"].unique())
        for column in columns:
            le = LabelEncoder()
            df[column] = le.fit_transform(df[column])
            les.append(le)
        return df, *les

    def make_branch(self, res_input, n_out, act_type, name):
        x = layers.Dense(512, activation="relu")(res_input)
        x = layers.Dense(256, activation='relu')(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dense(64, activation='relu')(x)

        x = layers.Dense(n_out)(x)
        x = layers.Activation(act_type, name=name)(x)
        return x
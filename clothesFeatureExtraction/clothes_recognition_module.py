import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import cv2
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing import image
from tensorflow.keras.utils import plot_model
import colorsys          
import base64                                           
import PIL.Image as Image
from scipy.spatial import KDTree
from webcolors import (
   CSS3_HEX_TO_NAMES,
    hex_to_rgb
)
from clothesFeatureExtraction.utils import (
       BODYWEAR,
       BOTTOMWEAR,
       FOOTWEAR,
       IMG_HEIGHT,
       IMG_WIDTH,
       LOCAL_PATH,
       TOPWEAR,
)
from clothesFeatureExtraction.subcategory_model import SubcategoryModel
from clothesFeatureExtraction.topwear_model import TopwearModel
from clothesFeatureExtraction.bottomwear_model import BottomwearModel
from clothesFeatureExtraction.footwear_model import FootwearModel
from clothesFeatureExtraction.bodywear_model import BodywearModel


def classify_cloth_image(image_path):
       img = cv2.imread(image_path)
       
       # resize the image if it's not the right size for the models
       if img.shape != (IMG_HEIGHT, IMG_WIDTH, 3):
              img = image.load_img(image_path, target_size=(IMG_HEIGHT, IMG_WIDTH, 3))
       
       # create a batch of 1 image to feed into the model
       test_images = np.zeros((1, IMG_HEIGHT, IMG_WIDTH, 3))
       test_images[0] = img
       plt.imshow(img)
       plt.show()
       subcategory_model = SubcategoryModel()
       subcategory_prediction = subcategory_model.get_model_prediction(test_images)
       print(subcategory_prediction)
       
       # get the model corresponding to the subcategory prediction
       model = None
       if subcategory_prediction == TOPWEAR:
              model = TopwearModel()
       elif subcategory_prediction == BOTTOMWEAR:
              model = BottomwearModel()
       elif subcategory_prediction == FOOTWEAR:
              model = FootwearModel()
       elif subcategory_prediction == BODYWEAR:
              model = BodywearModel()

       return model.get_model_prediction(test_images)
       

def classify_cloth_image_from_base64(b64_image_string):
       b64_image_string = b64_image_string[len("data:image/jpeg;base64,"):]
       img_data = base64.b64decode(b64_image_string)
       # Convert this data into a format that OpenCV can read
       img_array = np.frombuffer(img_data, dtype=np.uint8)
       print(img_array)
       img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
       
       # resize the image if it's not the right size for the models
       if img.shape != (IMG_HEIGHT, IMG_WIDTH, 3):
              img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT), interpolation=cv2.INTER_LINEAR)
       
       # create a batch of 1 image to feed into the model
       test_images = np.zeros((1, IMG_HEIGHT, IMG_WIDTH, 3))
       test_images[0] = img
       # cv2.imshow('asd', img)
       # cv2.waitKey(0)
       subcategory_model = SubcategoryModel()
       subcategory_prediction = subcategory_model.get_model_prediction(test_images)
       print(subcategory_prediction)
       
       # get the model corresponding to the subcategory prediction
       model = None
       if subcategory_prediction == TOPWEAR:
              model = TopwearModel()
       elif subcategory_prediction == BOTTOMWEAR:
              model = BottomwearModel()
       elif subcategory_prediction == FOOTWEAR:
              model = FootwearModel()
       elif subcategory_prediction == BODYWEAR:
              model = BodywearModel()

       return model.get_model_prediction(test_images)

def main():
       print(classify_cloth_image(LOCAL_PATH + r"\garderoba\pantofi2.jpg"))

# pantaloni -> topwear, footwear
# bluza -> footwear
# pantofi -> bottomwear

if __name__ == "__main__":
       print("Start")
       main()
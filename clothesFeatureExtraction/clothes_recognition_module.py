import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import cv2
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import GaussianNB
from sklearn.utils.class_weight import compute_class_weight
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing import image
from tensorflow.keras.utils import plot_model
from tensorflow.keras.models import load_model
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

def classify_from_base64(b64_image_string, model_path, class_names):
    model = load_model(model_path)
    b64_image_string = b64_image_string[len("data:image/jpeg;base64,"):]
    image_binary = base64.b64decode(b64_image_string)
    
    img = tf.io.decode_image(image_binary, channels=3)
    img = tf.image.resize(img, size=[224, 224])
    img = img / 255.
    pred = model.predict(tf.expand_dims(img, axis=0))
    pred_class = None
    if len(pred[0]) > 1: # check for multi-class
        pred_class = class_names[pred.argmax()] # if more than one output, take the max
    else:
        pred_class = class_names[int(tf.round(pred)[0][0])]
    print(pred_class)
    return pred_class
    
def classify_category_from_b64(b64_image_string):
    category_class_names = ['Accessories', 'Bodywear', 'Bottomwear', 'Footwear', 'Headwear', 'Topwear'] # 6 classes
    return classify_from_base64(b64_image_string, 'models/category_classification.h5', category_class_names)

def classify_subcategory_from_b64(b64_image_string, category):
    article_type_class_names = [
        'Shirts', 'Jeans', 'Watches', 'Track Pants', 'Tshirts', 'Casual Shoes', 'Belts', 'Flip Flops',
        'Handbags', 'Tops', 'Sandals', 'Sweatshirts', 'Formal Shoes', 'Bracelet', 'Flats', 'Waistcoat',
        'Sports Shoes', 'Shorts', 'Heels', 'Pendant', 'Dresses', 'Skirts', 'Blazers', 'Ring',
        'Clutches', 'Shrug', 'Backpacks', 'Caps', 'Trousers', 'Earrings', 'Jewellery Set', 'Capris',
        'Tunics', 'Jackets', 'Necklace and Chains', 'Duffel Bag', 'Sports Sandals', 'Sweaters', 'Tracksuits', 'Swimwear',
        'Ties', 'Leggings', 'Travel Accessory', 'Mobile Pouch', 'Messenger Bag', 'Accessory Gift Set', 'Jumpsuit', 'Suspenders',
        'Patiala', 'Stockings', 'Headband', 'Tights', 'Tablet Sleeve', 'Nehru Jackets', 'Salwar', 'Jeggings',
        'Rompers', 'Waist Pouch', 'Hair Accessory', 'Rucksacks', 'Key chain', 'Rain Jacket', 'Water Bottle', 'Hat',
        'Suits'
    ] # 65 classes
    model_path = 'models/subcategory_classification.h5'
    if category == "Topwear":
        print("in Topwear")
        model_path = 'models/subcategory_classification_topwear.h5'
        
    return classify_from_base64(b64_image_string, model_path, article_type_class_names)

def classify_season_from_b64(b64_image_string):
    season_class_names = ['Summer', 'Winter', 'Spring', 'Autumn'] # 4 classes
    return classify_from_base64(b64_image_string, 'models/season_classification.h5', season_class_names)

def classify_color_from_b64(b64_image_string):
    color_class_names = [
        "Navy Blue", "Blue", "Silver", "Black", "Grey", "Green", "Purple", "White", "Brown",
        "Bronze", "Teal", "Copper", "Pink", "Off White", "Beige", "Red", "Khaki", "Orange", 
        "Yellow", "Charcoal", "Steel", "Gold", "Tan", "Magenta", "Lavender", "Sea Green", 
        "Cream", "Peach", "Olive", "Burgundy", "Multi", "Maroon", "Grey Melange", "Rust", 
        "Turquoise Blue", "Metallic", "Mustard", "Coffee Brown", "Taupe", "Mauve", 
        "Mushroom Brown", "Nude", "Fluorescent Green", "Lime Green", "Rose"
    ] # 45 classes
    return classify_from_base64(b64_image_string, 'models/base_color_classification.h5', color_class_names)

def classify_usage_from_b64(b64_image_string):
    usage_class_names =['Casual', 'Ethnic', 'Formal', 'Sports', 'Smart Casual', 'Travel', 'Party'] # 7 classes
    return classify_from_base64(b64_image_string, 'models/usage_classification.h5', usage_class_names)

def calc_wear_probability(number, mu=10, sigma=5):
    return np.exp(-((number - mu) ** 2) / (2 * sigma ** 2))

def calc_mean(temperature_probability, weather_prob):
    return (temperature_probability + weather_prob) / 2


def normalize_percentages(percentages):
        total_sum = sum(percentages)
        normalization_factor = 100 / total_sum
        normalized_percentages = [round(p * normalization_factor, 2) for p in percentages]
        
        while sum(normalized_percentages) != 100:
            for i in range(len(normalized_percentages)):
                if sum(normalized_percentages) < 100:
                    normalized_percentages[i] += 0.01
                    normalized_percentages[i] = round(normalized_percentages[i], 2)
                    if sum(normalized_percentages) == 100:
                        break
                elif sum(normalized_percentages) > 100:
                    normalized_percentages[i] -= 0.01
                    normalized_percentages[i] = round(normalized_percentages[i], 2)
                    if sum(normalized_percentages) == 100:
                        break
        
        return normalized_percentages

# def get_outfit_recommendation(likelihoods):
#     for item in items:
#         p_item = len([i for i in items if i == p_item]) / len(items)
#         p_weather = len([i for i in p_weathers if i == p_weathers]) / len(p_weathers)
#         calculate_posterior(p_item, likelihood, p_weather)

# def calculate_posterior(prior, likelihood, evidence):
#     """
#     Calculate the posterior probability using Bayes' Theorem.

#     :param prior: Prior probability of the hypothesis (P(H)).
#     :param likelihood: Probability of the evidence given the hypothesis (P(E|H)).
#     :param evidence: Total probability of the evidence (P(E)).
#     :return: Posterior probability (P(H|E)).
#     """
#     return (likelihood * prior) / evidence

# # Define the probabilities
# # Priors (Assuming equal probability for demonstration)
# priors = {'Cold and Snowy': 0.5, 'Hot and Sunny': 0.5}

# # Likelihoods
# likelihoods = {
#     'Coat': {'Cold and Snowy': 0.95, 'Hot and Sunny': 0.05},
#     'Shorts': {'Cold and Snowy': 0.05, 'Hot and Sunny': 0.95}
# }

# # Evidence (calculated as the sum of the product of prior and likelihood for each hypothesis)
# evidence = {
#     scenario: sum(priors[hypothesis] * likelihoods[clothing_item][hypothesis] 
#                   for hypothesis in priors for clothing_item in likelihoods)
#     for scenario in priors
# }

# # Calculate posterior probabilities for each clothing item in each scenario
# posterior_probabilities = {
#     clothing_item: {
#         scenario: calculate_posterior(priors[scenario], likelihoods[clothing_item][scenario], evidence[scenario])
#         for scenario in priors
#     } for clothing_item in likelihoods
# }

# # Output the calculated posterior probabilities
# for clothing_item in posterior_probabilities:
#     for scenario in posterior_probabilities[clothing_item]:
#         print(f"P({clothing_item}|{scenario}) = {posterior_probabilities[clothing_item][scenario]:.2f}")

    

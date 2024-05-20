# import pandas as pd
# import matplotlib.pyplot as plt
import numpy as np
# import cv2
import torch
import clip
from io import BytesIO
# import colorsys          
import base64                                           
import PIL.Image as Image
# import clothesFeatureExtraction.color_module as color_module
# from scipy.spatial import KDTree
# from webcolors import (
#     CSS3_HEX_TO_NAMES,
#     hex_to_rgb
# )
# from clothesFeatureExtraction.utils import (
#     BODYWEAR,
#     BOTTOMWEAR,
#     FOOTWEAR,
#     IMG_HEIGHT,
#     IMG_WIDTH,
#     LOCAL_PATH,
#     TOPWEAR,
# )
# from clothesFeatureExtraction.subcategory_model import SubcategoryModel
# from clothesFeatureExtraction.topwear_model import TopwearModel
# from clothesFeatureExtraction.bottomwear_model import BottomwearModel
# from clothesFeatureExtraction.footwear_model import FootwearModel
# from clothesFeatureExtraction.bodywear_model import BodywearModel
from clothesFeatureExtraction.similarity import Similarity

clip_device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, clip_preprocess = clip.load("ViT-B/32", device=clip_device)

# def classify_cloth_image(image_path):
#     img = cv2.imread(image_path)
    
#     # resize the image if it's not the right size for the models
#     if img.shape != (IMG_HEIGHT, IMG_WIDTH, 3):
#         img = image.load_img(image_path, target_size=(IMG_HEIGHT, IMG_WIDTH, 3))
    
#     # create a batch of 1 image to feed into the model
#     test_images = np.zeros((1, IMG_HEIGHT, IMG_WIDTH, 3))
#     test_images[0] = img
#     plt.imshow(img)
#     plt.show()
#     subcategory_model = SubcategoryModel()
#     subcategory_prediction = subcategory_model.get_model_prediction(test_images)
#     print(subcategory_prediction)
    
#     # get the model corresponding to the subcategory prediction
#     model = None
#     if subcategory_prediction == TOPWEAR:
#         model = TopwearModel()
#     elif subcategory_prediction == BOTTOMWEAR:
#         model = BottomwearModel()
#     elif subcategory_prediction == FOOTWEAR:
#         model = FootwearModel()
#     elif subcategory_prediction == BODYWEAR:
#         model = BodywearModel()

#     return model.get_model_prediction(test_images)
       

# def classify_cloth_image_from_base64(b64_image_string):
#     b64_image_string = b64_image_string[len("data:image/jpeg;base64,"):]
#     img_data = base64.b64decode(b64_image_string)
#     # Convert this data into a format that OpenCV can read
#     img_array = np.frombuffer(img_data, dtype=np.uint8)
#     print(img_array)
#     img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
#     # resize the image if it's not the right size for the models
#     if img.shape != (IMG_HEIGHT, IMG_WIDTH, 3):
#         img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT), interpolation=cv2.INTER_LINEAR)
    
#     # create a batch of 1 image to feed into the model
#     test_images = np.zeros((1, IMG_HEIGHT, IMG_WIDTH, 3))
#     test_images[0] = img
#     # cv2.imshow('asd', img)
#     # cv2.waitKey(0)
#     subcategory_model = SubcategoryModel()
#     subcategory_prediction = subcategory_model.get_model_prediction(test_images)
#     print(subcategory_prediction)
    
#     # get the model corresponding to the subcategory prediction
#     model = None
#     if subcategory_prediction == TOPWEAR:
#         model = TopwearModel()
#     elif subcategory_prediction == BOTTOMWEAR:
#         model = BottomwearModel()
#     elif subcategory_prediction == FOOTWEAR:
#         model = FootwearModel()
#     elif subcategory_prediction == BODYWEAR:
#         model = BodywearModel()

#     return model.get_model_prediction(test_images)

# def classify_from_base64(b64_image_string, model_path, class_names):
#     model = load_model(model_path)
#     b64_image_string = b64_image_string[len("data:image/jpeg;base64,"):]
#     image_binary = base64.b64decode(b64_image_string)
    
#     img = tf.io.decode_image(image_binary, channels=3)
#     img = tf.image.resize(img, size=[224, 224])
#     img = img / 255.
#     pred = model.predict(tf.expand_dims(img, axis=0))
#     pred_class = None
#     if len(pred[0]) > 1: # check for multi-class
#         pred_class = class_names[pred.argmax()] # if more than one output, take the max
#     else:
#         pred_class = class_names[int(tf.round(pred)[0][0])]
#     print(pred_class)
#     return pred_class
    
# def classify_category_from_b64(b64_image_string):
#     category_class_names = ['Accessories', 'Bodywear', 'Bottomwear', 'Footwear', 'Headwear', 'Topwear'] # 6 classes
#     return classify_from_base64(b64_image_string, 'models/category_classification.h5', category_class_names)

# def classify_subcategory_from_b64(b64_image_string, category):
#     article_type_class_names = [
#         'Shirts', 'Jeans', 'Watches', 'Track Pants', 'Tshirts', 'Casual Shoes', 'Belts', 'Flip Flops',
#         'Handbags', 'Tops', 'Sandals', 'Sweatshirts', 'Formal Shoes', 'Bracelet', 'Flats', 'Waistcoat',
#         'Sports Shoes', 'Shorts', 'Heels', 'Pendant', 'Dresses', 'Skirts', 'Blazers', 'Ring',
#         'Clutches', 'Shrug', 'Backpacks', 'Caps', 'Trousers', 'Earrings', 'Jewellery Set', 'Capris',
#         'Tunics', 'Jackets', 'Necklace and Chains', 'Duffel Bag', 'Sports Sandals', 'Sweaters', 'Tracksuits', 'Swimwear',
#         'Ties', 'Leggings', 'Travel Accessory', 'Mobile Pouch', 'Messenger Bag', 'Accessory Gift Set', 'Jumpsuit', 'Suspenders',
#         'Patiala', 'Stockings', 'Headband', 'Tights', 'Tablet Sleeve', 'Nehru Jackets', 'Salwar', 'Jeggings',
#         'Rompers', 'Waist Pouch', 'Hair Accessory', 'Rucksacks', 'Key chain', 'Rain Jacket', 'Water Bottle', 'Hat',
#         'Suits'
#     ] # 65 classes
#     model_path = 'models/subcategory_classification.h5'
#     if category == "Topwear":
#         print("in Topwear")
#         model_path = 'models/subcategory_classification_topwear.h5'
        
#     return classify_from_base64(b64_image_string, model_path, article_type_class_names)

# def classify_season_from_b64(b64_image_string):
#     season_class_names = ['Summer', 'Winter', 'Spring', 'Autumn'] # 4 classes
#     return classify_from_base64(b64_image_string, 'models/season_classification.h5', season_class_names)

# def classify_color_from_b64(b64_image_string):
#     return color_module.color_classification_b64(b64_image_string)

# def classify_usage_from_b64(b64_image_string):
#     usage_class_names =['Casual', 'Ethnic', 'Formal', 'Sports', 'Smart Casual', 'Travel', 'Party'] # 7 classes
#     return classify_from_base64(b64_image_string, 'models/usage_classification.h5', usage_class_names)

def calc_wear_probability(number, mu=10, sigma=5):
    # scaling_factor = 1 / (np.sqrt(2 * np.pi * sigma ** 2))
    # return scaling_factor * np.exp(-((number - mu) ** 2) / (2 * sigma ** 2))
    return np.exp(-((number - mu) ** 2) / (2 * sigma ** 2))

def calc_mean(temperature_probability, weather_prob):
    return (temperature_probability + weather_prob) / 2


def normalize_percentages(percentages):
        total_sum = sum(percentages)
        if total_sum == 0:
            normalized_percentages = [round(100 / len(percentages), 2) for _ in percentages]
        else:
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

def normalize_probabilities(probabilities):
    total_sum = sum(probabilities)
    if total_sum == 0:
        normalized_probabilities = [1 / len(probabilities) for _ in probabilities]
    else:
        normalization_factor = 1 / total_sum
        normalized_probabilities = [round(p * normalization_factor, 6) for p in probabilities]
    
    while sum(normalized_probabilities) != 1.0:
        for i in range(len(normalized_probabilities)):
            if sum(normalized_probabilities) < 1.0:
                normalized_probabilities[i] += 0.000001
                normalized_probabilities[i] = round(normalized_probabilities[i], 6)
                if sum(normalized_probabilities) == 1.0:
                    break
            elif sum(normalized_probabilities) > 1.0:
                normalized_probabilities[i] -= 0.000001
                normalized_probabilities[i] = round(normalized_probabilities[i], 6)
                if sum(normalized_probabilities) == 1.0:
                    break

    return normalized_probabilities

def use_clip(labels, image_b64):
    image_data = base64.b64decode(image_b64[image_b64.find(','):])
    image = clip_preprocess(Image.open(BytesIO(image_data))).unsqueeze(0).to(clip_device)
    text = clip.tokenize(labels).to(clip_device)
    with torch.no_grad():
        image_features = clip_model.encode_image(image)
        text_features = clip_model.encode_text(text)
        
        logits_per_image, logits_per_text = clip_model(image, text)
        probs = logits_per_image.softmax(dim=-1).cpu().numpy()

    print(probs)
    return labels[np.argmax(probs)]

def calculate_similarity(item, all_items):
    return Similarity().get_top_similar_items(item, all_items)
    

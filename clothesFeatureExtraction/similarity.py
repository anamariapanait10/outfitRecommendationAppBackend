from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
import tensorflow as tf
import numpy as np
import base64
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import cosine_similarity


class Similarity:
    def __init__(self):
        self.model = None
        self.load_model()
        
    def load_model(self):
        base_model = ResNet50(weights='imagenet')
        self.model = Model(inputs=base_model.input, outputs=base_model.get_layer('avg_pool').output)

    def extract_features(self, b64_image_string):
        b64_image_string = b64_image_string[len("data:image/jpeg;base64,"):]
        image_binary = base64.b64decode(b64_image_string)
        img = tf.io.decode_image(image_binary, channels=3)
        img = tf.image.resize(img, size=[224, 224])
        img = img / 255.
        features = self.model.predict(tf.expand_dims(img, axis=0))

        return features.flatten()
    
    def calculate_similarity(self, base_item, candidate_items):
        descriptions = [base_item.description] + [item.description for item in candidate_items]

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(descriptions)

        cos_similarities_description = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        # compute score for categorical attributes
        match_scores = []
        for item in candidate_items:
            score = 0
            score += (base_item.size == item.size)
            score += (base_item.brand == item.brand)
            score += (base_item.outfit.color == item.outfit.color)
            score += (base_item.outfit.category == item.outfit.category)
            match_scores.append(score / 4)
        
        # calculate visual similarities
        base_features = self.extract_features(base_item.outfit.image)
        visual_similarities = []
        for item in candidate_items:
            candidate_features = self.extract_features(item.outfit.image)
            visual_similarity = cosine_similarity([base_features], [candidate_features])[0][0]
            visual_similarities.append(visual_similarity)

        combined_scores = 0.4 * np.array(cos_similarities_description) + 0.4 * np.array(visual_similarities) + 0.2 * np.array(match_scores)
        return combined_scores

    def get_top_similar_items(self, base_item, candidate_items, num_results=3):
        similarities = self.calculate_similarity(base_item, list(candidate_items))
        top_indices = np.argsort(-similarities)[:num_results]
        top_items = [candidate_items[int(i)] for i in top_indices]
        return top_items
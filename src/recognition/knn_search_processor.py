import os
import pickle
import json
import numpy as np


class KnnSearchProcessor:
    knn_model_path = os.path.join(os.getcwd(), "src/models/knn/knn_model.pkl")
    index_path = os.path.join(os.getcwd(), "src/models/knn/index.json")
    distance_threshold = 0.6

    def __init__(self):
        # Load the NearestNeighbors object from a file
        with open(self.knn_model_path, 'rb') as f:
            loaded_knn_model = pickle.load(f)

        # Load the dictionary from the file
        with open(self.index_path, 'r') as f:
            loaded_index = json.load(f)

        self.knn_model = loaded_knn_model
        self.index_vs_id_dict = {int(k): v for k, v in loaded_index.items()}

    def search(self, embeddings):
        unknown_person_embedding = embeddings[0, :].reshape(
            1, -1)
        distances, indices = self.knn_model.kneighbors(
            unknown_person_embedding)
        min_distance_index = np.argmin(distances, axis=1)
        min_distance_value = distances[0, min_distance_index]
        if min_distance_value > self.distance_threshold:
            return None
        index = indices[0, min_distance_index]
        matched_person_id = self.index_vs_id_dict[index[0]]
        return matched_person_id

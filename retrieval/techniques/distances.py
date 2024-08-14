import math
import numpy as np
import os
from PIL import Image
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from process import read_image_from_path, get_single_image_embedding, folder_to_images




def absolute_difference(query, data):
    axis_batch_size = tuple(range(1, len(data.shape)))
    return np.sum(np.abs(data - query), axis = axis_batch_size)


def mean_square_difference(query, data):
    axis_batch_size = tuple(range(1, len(data.shape)))
    return np.mean((data - query)**2, axis = axis_batch_size)


def cosine_similarity(query, data):
    axis_batch_size = tuple(range(1, len(data.shape)))
    query_norm = np.sqrt(np.sum(query**2))
    data_norm = np.sqrt(np.sum(data**2, axis = axis_batch_size))
    return np.sum(data * query, axis = axis_batch_size) / (query_norm * data_norm + np.finfo(float).eps)


def correlation_coefficient(query, data):
    axis_batch_size = tuple(range(1, len(data.shape)))
    query_mean = query - np.mean(query)
    data_mean = data - np.mean(data, axis = axis_batch_size, keepdims=True)
    query_norm = np.sqrt(np.sum(query_mean**2))
    data_norm = np.sqrt(np.sum(data_mean**2, axis = axis_batch_size))
    return np.sum(data_mean * query_mean, axis = axis_batch_size) / (query_norm * data_norm + np.finfo(float).eps)


def get_score(root_image_path: str, query_path: str,
              size: tuple, kernel: str, classname: list):
    """
    kernel: "l1", "l2", "cosine", "correlation"
    """
    query = read_image_from_path(query_path, size)
    ls_path_score = []
    
    for folder in os.listdir(root_image_path):
        if folder in classname:
            path = root_image_path + folder
            images_np, images_path = folder_to_images(path, size)

            embedding_list = []
            for idx_img in range(images_np.shape[0]):
                embedding = get_single_image_embedding(images_np[idx_img].astype(np.uint8))
                embedding_list.append(embedding)

            if kernel == "l1":
                rates = absolute_difference(query, np.stack(embedding_list))
            elif kernel == "l2":
                rates = mean_square_difference(query, np.stack(embedding_list))
            elif kernel == "cosine":
                rates = cosine_similarity(query, np.stack(embedding_list))
            elif kernel == "correlation":
                rates = correlation_coefficient(query, np.stack(embedding_list))
            
            ls_path_score.extend(list(zip(images_path, rates)))
    
    return query, ls_path_score
import math
import numpy as np
import os
import json
from PIL import Image
import matplotlib.pyplot as plt
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
import chromadb
import tqdm
from process import get_single_image_embedding, get_files_path




def add_embedding(file_path: list,
                  distance: str):
    
    """
    filepath: list of image paths
    distance: "l2", "cosine"
    """

    chroma_client = chromadb.Client()

    if distance == "l2":
        collection = chroma_client.get_or_create_collection(name = "l2_collection",
                                                            metadata={"hnsw:space": "l2"})
    
    elif distance == "cosine":
        collection = chroma_client.get_or_create_collection(name = "cosine_collection",
                                                            metadata={"hnsw:space": "cosine"})
    else:
        raise ValueError("Only two distance methods: 'consine' and 'l2' ")
    
    ids = []
    embeddings = []
    for id_filepath, filepath in tqdm(enumerate(file_path)):
        ids.append(f"id_{id_filepath}")
        image = Image.open(filepath)
        
        embedding = get_single_image_embedding(image=image)
        embeddings.append(embedding)
    
    collection.add(embeddings=embeddings,
                   ids=ids)
    
    return collection

def build_collector(file_path: str, distance: str):
    url_path = get_files_path(path = file_path)

    collection = add_embedding(file_path = url_path, distance = distance)

    return collection


def search(image_path: str, collection, n_results):
    """
    image_path: query image
    collection: embedding vector database
    """
    query_image = Image.open(image_path)
    query_embedding = get_single_image_embedding(query_image)
    results = collection.query(
        query_embeddings = [query_embedding],
        n_results = n_results
    )

    return results
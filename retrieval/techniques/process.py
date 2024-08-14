import numpy as np
import os
import json
from PIL import Image
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
import matplotlib.pyplot as plt


data_cfg = "./cfg/data.json"

with open(data_cfg, "r") as f:
    data = json.load(f)

labels = data["labels"]
keys = list(labels.keys())
CLASSNAME = []

for i in range(len(keys)):
    CLASSNAME += labels[keys[i]]


def get_files_path(path):
    files_path = []
    for label in CLASSNAME:
        label_path = path + "/" + label
        filenames = os.listdir(label_path)
        for filename in filenames:
            filepath = label_path + "/" + filename
            files_path.append(filepath)
    
    return files_path


def read_image_from_path(path: str, size: tuple):
    im = Image.open(path).convert("RGB").resize(size)
    return np.array(im)


def folder_to_images(folder, size):
    list_dir = [folder + "/" + name for name in os.listdir(folder)]
    images_np = np.zeros(shape=(len(list_dir), *size, 3))
    images_path = []
    for i, path in enumerate(list_dir):
        images_np[i] = read_image_from_path(path, size)
        images_path.append(path)

    images_path = np.array(images_path)
    return images_np, images_path                         
                    
embedding_function = OpenCLIPEmbeddingFunction()

def get_single_image_embedding(image):
    embedding = embedding_function._encode_image(image=image)
    return np.array(embedding)


def plot_results(image_path: str, files_path: list, results):
    """
    image_path: image URL to query
    files_path: list of image URL to reference (image URL of embedding vector)
    """
    
    query_image = Image.open(image_path).resize((448,448))
    images = [query_image]
    class_name = []
    for id_img in results['ids'][0]:
        id_img = int(id_img.split('_')[-1])
        img_path = files_path[id_img]
        img = Image.open(img_path).resize((448,448))
        images.append(img)
        class_name.append(img_path.split('/')[2])

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))

    # Iterate through images and plot them
    for i, ax in enumerate(axes.flat):
        ax.imshow(images[i])
        if i == 0:
            ax.set_title(f"Query Image: {image_path.split('/')[2]}")
        else:
            ax.set_title(f"Top {i+1}: {class_name[i-1]}")
        ax.axis('off')  # Hide axes
    # Display the plot
    plt.show()
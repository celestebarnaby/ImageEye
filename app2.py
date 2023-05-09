import os
# import faiss
import torch
# import skimage
import requests
# import pinecone
from PIL import Image
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
from PIL import Image
from utils import *
from sklearn.metrics.pairwise import cosine_similarity
import subprocess
from flask import Flask, request, jsonify
from utils import *
from synthesizer import *
import torch
import numpy as np
from PIL import Image

from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
img_to_environment = {}
img_to_embedding = {}


def get_model_info(model_ID, device):
    # Save the model to device
    model = CLIPModel.from_pretrained(model_ID).to(device)
    # Get the processor
    processor = CLIPProcessor.from_pretrained(model_ID)
# Get the tokenizer
    tokenizer = CLIPTokenizer.from_pretrained(model_ID)
   # Return model, processor & tokenizer
    return model, processor, tokenizer


# Set the device
device = "cuda" if torch.cuda.is_available() else "cpu"
# Define the model ID
model_ID = "openai/clip-vit-base-patch32"
# Get model, processor & tokenizer
model, processor, tokenizer = get_model_info(model_ID, device)


def get_text_embedding(text):
    inputs = tokenizer(text, return_tensors="pt")
    text_embeddings = model.get_text_features(**inputs)
    # convert the embeddings to numpy array
    embedding_as_np = text_embeddings.cpu().detach().numpy()
    return embedding_as_np


def get_image_embedding(image):
    image = processor(
        text=None,
        images=image,
        return_tensors="pt"
    )["pixel_values"].to(device)
    embedding = model.get_image_features(image)
    embedding_as_np = embedding.cpu().detach().numpy()
    return embedding_as_np


@app.route("/textQuery", methods=['POST'])
@cross_origin()
def text_query():
    global img_to_environment

    text_query = request.get_json()
    results = get_top_N_images(text_query)
    return {
        'search_results': results,
        # 'sidebarFiles': [filename for filename in imgs][:5]
    }


@app.route("/imageQuery", methods=['POST'])
@cross_origin()
def image_query():
    global img_to_embedding

    image_name = request.get_json()
    image = img_to_embedding[image_name][0]
    results = get_top_N_images(image, search_criterion="image")
    return {
        'search_results': results,
        # 'sidebarFiles': [filename for filename in imgs][:5]
    }


def get_top_N_images(query, top_K=4, search_criterion="text"):
    global img_to_embedding
    image_names = img_to_embedding.keys()
    image_embeddings = [img_to_embedding[name][1]
                        for name in image_names]

   # Text to image Search
    if search_criterion.lower() == "text":
        query_vect = get_text_embedding(query)
    # Image to image Search
    else:
        query_vect = get_image_embedding(query)
    # Run similarity Search
    cos_sim = [cosine_similarity(query_vect, x) for x in image_embeddings]
    cos_sim = [x[0][0] for x in cos_sim]
    cos_sim_per_image = zip(cos_sim, image_names)
    most_similar = sorted(cos_sim_per_image, reverse=True)
    # [1:top_K+1]  # line 24
    top_images = [img for (_, img) in most_similar]
    return top_images


@app.route("/loadFiles", methods=['POST'])
@cross_origin()
def load_files():
    global img_to_environment
    global obj_strs
    global img_to_embedding
    data = request.get_json()
    img_to_environment, obj_strs = preprocess(
        "image-eye-web/public/images/" + data + "/", 100)
    consolidate_environment(img_to_environment)
    add_descriptions(img_to_environment)
    for image_name in img_to_environment:
        image = Image.open(image_name)
        img_to_embedding[image_name] = (image, get_image_embedding(image))
    return {
        'message': img_to_environment,
        'files': [filename for filename in img_to_environment.keys()]
    }


if __name__ == "__main__":
    app.run(debug=True)

import os
import torch
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
from utils import *
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify
from utils import *
from synthesizer import *
import torch
import numpy as np
import time

from flask_cors import CORS, cross_origin
from PIL import Image

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
img_to_environment = {}
img_to_embedding = {}
logged_info = {}


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
    global logged_info

    text_query = request.get_json()
    logged_info["text queries"].append(text_query)
    results = get_top_N_images(text_query)
    return {
        'search_results': results,
        # 'sidebarFiles': [filename for filename in imgs][:5]
    }


@app.route("/imageQuery", methods=['POST'])
@cross_origin()
def image_query():
    global img_to_embedding
    global logged_info

    image_name = request.get_json()
    logged_info["image queries"].append(image_name)
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
    threshold = .2 if search_criterion == "text" else .75

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
    print(most_similar)
    # [1:top_K+1]  # line 24
    top_images = [img for (cos_sim, img)
                  in most_similar if cos_sim > threshold]
    return top_images


@app.route("/loadFiles", methods=['POST'])
@cross_origin()
def load_files():
    global img_to_environment
    global obj_strs
    global img_to_embedding
    global logged_info
    task_num = request.get_json()
    num_to_task = {
        1: {"description": "Find all images featuring a person riding a bicycle", "dataset": "objects"},
        2: {"description": "Find all images where Bob is smiling", "dataset": "wedding2"}
    }
    task = num_to_task[task_num]
    img_to_embedding = {}
    img_to_environment, obj_strs = preprocess(
        "image-eye-web/public/images/" + task["dataset"] + "/", 100)
    consolidate_environment(img_to_environment)
    add_descriptions(img_to_environment)
    for image_name in img_to_environment:
        image = Image.open(image_name)
        img_to_embedding[image_name] = (image, get_image_embedding(image))
    logged_info["task"] = task["description"]
    logged_info["dataset"] = task["dataset"]
    logged_info["text queries"] = []
    logged_info["image queries"] = []
    logged_info["num"] = task_num
    logged_info["start time"] = time.perf_counter()
    return {
        'message': img_to_environment,
        'files': [filename for filename in img_to_environment.keys()],
        'task_description': task["description"]
    }


@app.route("/submitResults", methods=['POST'])
@cross_origin()
def log_results():
    global img_to_environment
    global obj_strs
    global img_to_embedding
    results = request.get_json()

    logged_info["end time"] = time.perf_counter()
    total_time = logged_info["end time"] - logged_info["start time"]
    name = "output_{}.csv".format(logged_info["num"])
    with open(name, "w") as f:
        fw = csv.writer(f)
        fw.writerow(
            (
                "Task",
                "Dataset",
                "Text Queries",
                "Image Queries",
                "Results",
                "Images Manually Added to Results",
                "Images Manually Removed from Results",
                "Total Time"
            ),
        )
        fw.writerow(
            (
                logged_info["task"],
                logged_info["dataset"],
                logged_info["text queries"],
                logged_info["image queries"],
                results["results"],
                results["manually_added"],
                results["manually_removed"],
                total_time
            )
        )


if __name__ == "__main__":
    app.run(debug=True)

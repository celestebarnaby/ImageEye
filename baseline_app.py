import os
import torch
from utils import *
from flask import Flask, request, jsonify
from utils import *
from synthesizer import *
import torch
import numpy as np
import time
from user_study_tasks import tasks

from flask_cors import CORS, cross_origin
from PIL import Image

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
img_to_environment = {}
img_to_embedding = {}
logged_info = {}


# Set the device
device = "cuda" if torch.cuda.is_available() else "cpu"
# Define the model ID
model_ID = "openai/clip-vit-base-patch32"
# Get model, processor & tokenizer
model, processor, tokenizer = get_model_info(model_ID, device)


@app.route("/textQuery", methods=['POST'])
@cross_origin()
def text_query():
    global img_to_environment
    global logged_info
    global img_to_embedding

    text_query = request.get_json()
    logged_info["text queries"].append(text_query)
    results = get_top_N_images(
        text_query, tokenizer, model, processor, device, img_to_embedding)
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
    image = Image.open(image_name)
    results = get_top_N_images(
        image, tokenizer, model, processor, device, img_to_embedding, search_criterion="image")
    return {
        'search_results': results,
        # 'sidebarFiles': [filename for filename in imgs][:5]
    }


@app.route("/loadFiles", methods=['POST'])
@cross_origin()
def load_files():
    global img_to_environment
    global obj_strs
    global img_to_embedding
    global logged_info
    task_num = request.get_json()
    task = tasks[task_num]
    img_to_embedding = {}
    img_folder = "image-eye-web/public/images/" + task["dataset"] + "/"
    img_to_environment, obj_strs = preprocess(
        img_folder, 100)
    consolidate_environment(img_to_environment)
    img_to_embedding = preprocess_embeddings(img_folder, img_to_environment, processor, device, model)
    # for image_name in img_to_environment:
    #     image = Image.open(image_name)
    #     img_to_embedding[image_name] = (
    #         image, get_image_embedding(image, processor, device, model))
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

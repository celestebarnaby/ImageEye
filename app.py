from flask import Flask, request, jsonify
from utils import *
from synthesizer import *
import torch
import numpy as np
from user_study_tasks import tasks
from PIL import Image

from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"
img_to_environment = {}
img_to_embedding = {}
logged_info = {}


# Set the device
device = "cuda" if torch.cuda.is_available() else "cpu"
# Define the model ID
model_ID = "openai/clip-vit-base-patch32"
# Get model, processor & tokenizer
model, processor, tokenizer = get_model_info(model_ID, device)


@app.route("/textQuery", methods=["POST"])
@cross_origin()
def text_query():
    global img_to_environment
    global logged_info
    global img_to_embedding

    text_query = request.get_json()
    logged_info["text queries"].append(text_query)
    results = get_top_N_images(
        text_query,
        tokenizer,
        model,
        processor,
        device,
        img_to_embedding,
        search_criterion="imageeye",
    )
    return {
        "files": results,
        # 'sidebarFiles': [filename for filename in imgs][:5]
    }


@app.route("/loadFiles", methods=["POST"])
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
    img_to_environment, obj_strs = preprocess(img_folder, 100)
    consolidate_environment(img_to_environment)
    img_to_embedding = preprocess_embeddings(
        img_folder, img_to_environment, processor, device, model
    )
    # img_to_embedding = get_img_to_embeddings(
    # img_folder, processor, device, model)
    logged_info["task"] = task["description"]
    logged_info["dataset"] = task["dataset"]
    logged_info["text queries"] = []
    logged_info["annotated images"] = []
    logged_info["num"] = task_num
    logged_info["start time"] = time.perf_counter()
    logged_info["synthesis_results"] = []
    return {
        "message": img_to_environment,
        "files": [filename for filename in img_to_environment.keys()],
        "task_description": task["description"],
    }


@cross_origin()
@app.route("/synthesize", methods=["POST"])
def get_synthesis_results():
    global img_to_environment
    global logged_info
    args = get_args()
    synth = Synthesizer(args, {})
    data = request.get_json()
    annotated_env = {}

    imgs = list(img_to_environment.keys())

    for img_dir, indices in data.items():
        logged_info["annotated images"].append(img_dir)
        annotated_env = (
            synth.get_environment(indices, img_dir, img_to_environment) | annotated_env
        )
    vector = np.array(get_img_vector(annotated_env.values(), obj_strs))
    # matrix = np.transpose(np.array([env["vector"]
    #   for env in img_to_environment.values()]))
    matrix = np.array([env["vector"] for env in img_to_environment.values()])

    cosine_similarities = np.dot(matrix, vector) / (
        np.linalg.norm(matrix, axis=1) * np.linalg.norm(vector)
    )
    indices = np.argsort(cosine_similarities)

    action = Blur()
    prog, _ = synth.synthesize_top_down(annotated_env, action, {}, args)
    if prog is None:
        response = {"program": None}
        return jsonify(response)
    results = []
    for img_dir, env in img_to_environment.items():
        env = env["environment"]
        output = eval_extractor(prog, env)
        if not output:
            continue
        # alt_img_dir = '.' + img_dir.split('/ui')[1]
        # results.append(alt_img_dir)
        results.append(img_dir)
    explanation = get_nl_explanation(prog)
    # alt_used_imgs = ['.' + img_dir.split('/ui')[1] for img_dir in data.keys()]
    used_imgs = list(data.keys())
    # images that are different from annotated images and in search results
    top_5_indices = []
    for i in indices:
        if len(top_5_indices) >= 5:
            break
        if imgs[i] in used_imgs:
            continue
        if imgs[i] in results:
            top_5_indices.append(imgs[i])
    # images that are similar to annotated images but NOT in search results
    bottom_5_indices = []
    for i in reversed(indices):
        if len(bottom_5_indices) >= 5:
            break
        if imgs[i] in used_imgs:
            continue
        if imgs[i] not in results:
            bottom_5_indices.append(imgs[i])
    recs = top_5_indices + bottom_5_indices
    logged_info["synthesis_results"].append(results)
    response = {"program": explanation, "search_results": results, "recs": recs}
    return jsonify(response)


@app.route("/submitResults", methods=["POST"])
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
                "Annotated Images",
                "Synthesis Results",
                "Submitted Images",
                "Images Manually Added to Results",
                "Images Manually Removed from Results",
                "Total Time",
            ),
        )
        fw.writerow(
            (
                logged_info["task"],
                logged_info["dataset"],
                logged_info["text queries"],
                logged_info["annotated images"],
                logged_info["synthesis_results"],
                results["results"],
                results["manually_added"],
                results["manually_removed"],
                total_time,
            )
        )
    response = {
        "status": "ok",
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="localhost", port=5001, debug=True)

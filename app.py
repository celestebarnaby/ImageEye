from flask import Flask, request, jsonify
from utils import *
from synthesizer import *
import torch
import clip
from PIL import Image
app = Flask(__name__)

img_to_environment = {}
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess_image = clip.load("ViT-B/32", device=device)
images = []

@app.route("/data")
def hello():
    global img_to_environment
    img_to_environment = preprocess("react-todo-app/src/components/ui/images/", 100)
    return {
        'message': img_to_environment
    }

@app.route("/textQuery", methods=['POST'])
def text_query():
    global img_to_environment
    global images
    text_query = request.get_json()
    text = clip.tokenize([text_query, "hi", "hello"]).to(device)
    print(text_query)
    with torch.no_grad():        
        logits_per_image, logits_per_text = model(images, text)
        print("get probs")
        probs = logits_per_image.softmax(dim=-1).cpu().numpy()
    probs = [prob[0] for prob in probs]
    print(len(img_to_environment.keys()))
    probs_and_imgs = zip(probs, img_to_environment.keys())
    probs_and_imgs = sorted(probs_and_imgs, reverse=True)
    print(probs_and_imgs)
    imgs = [img for (prob, img) in probs_and_imgs]
    return {
        'files': ["." + filename.split("ui")[1] for filename in imgs]
    }


@app.route("/loadFiles", methods=['POST'])
def load_files():
    global img_to_environment
    global images
    data = request.get_json()
    print('preprocess1')
    img_to_environment = preprocess("react-todo-app/src/components/ui/images/" + data + "/", 100)
    print('preprocess2')
    images = [preprocess_image(Image.open(image)).unsqueeze(0).to(device) for image in img_to_environment.keys()]
    images = torch.cat(images, dim=0)  
    return {
        'message': img_to_environment,
        'files': ["." + filename.split("ui")[1] for filename in img_to_environment.keys()]
    }

@app.route("/synthesize", methods=['POST'])
def get_synthesis_results():
    global img_to_environment
    args = get_args()
    client = get_client()
    client.delete_collection(CollectionId="library")
    client.create_collection(CollectionId="library")
    synth = Synthesizer(args, client, {})
    data = request.get_json()
    annotated_env = {}
    for (img_dir, indices) in data.items():
        annotated_env = (
            synth.get_environment(
                indices, img_dir, img_to_environment
            )
            | annotated_env
        )
    action = Blur()
    prog, num_progs = synth.synthesize_top_down(annotated_env, action, {}, args)
    results = []
    for img_dir, env in img_to_environment.items():
        env = env['environment']
        output = eval_extractor(prog, env)
        if not output:
            continue
        alt_img_dir = '.' + img_dir.split('ui')[1]
        results.append(alt_img_dir)
    print('will this work?')
    print(str(prog))
    response = {
        'program': str(prog),
        'results': results
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
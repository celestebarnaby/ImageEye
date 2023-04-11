import subprocess
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
        'searchResults': ["." + filename.split("ui")[1] for filename in imgs],
        'sidebarFiles': ["." + filename.split("ui")[1] for filename in imgs][:5]
    }


@app.route("/loadFiles", methods=['POST'])
def load_files():
    global img_to_environment
    global images
    data = request.get_json()
    img_to_environment = preprocess(
        "react-todo-app/src/components/ui/images/" + data + "/", 100)
    consolidate_environment(img_to_environment)
    images = [preprocess_image(Image.open(image)).unsqueeze(
        0).to(device) for image in img_to_environment.keys()]
    images = torch.cat(images, dim=0)
    return {
        'message': img_to_environment,
        'files': ["." + filename.split("ui")[1] for filename in img_to_environment.keys()]
    }


@app.route("/synthesize", methods=['POST'])
def get_synthesis_results():
    global img_to_environment
    args = get_args()
    synth = Synthesizer(args, {})
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
    prog, _ = synth.synthesize_top_down(
        annotated_env, action, {}, args)
    if prog is None:
        response = {
            'program': None
        }
        return jsonify(response)
    results = []
    for img_dir, env in img_to_environment.items():
        env = env['environment']
        output = eval_extractor(prog, env)
        if not output:
            continue
        alt_img_dir = '.' + img_dir.split('ui')[1]
        results.append(alt_img_dir)
    explanation = get_nl_explanation(prog).capitalize() + "."
    response = {
        'program': explanation,
        'searchResults': results,
        'sidebarFiles': results[:5]
    }
    return jsonify(response)


def get_nl_explanation(prog, neg=False):
    not_text = "not " if neg else ""
    if isinstance(prog, Union):
        sub_expls = [get_nl_explanation(sub_prog, neg)
                     for sub_prog in prog.extractors]
        if neg:
            return " and ".join(sub_expls)
        return " or ".join(sub_expls)
    if isinstance(prog, Intersection):
        sub_expls = [get_nl_explanation(sub_prog, neg)
                     for sub_prog in prog.extractors]
        if neg:
            return " or ".join(sub_expls)
        return " and ".join(sub_expls)
    if isinstance(prog, IsFace):
        return "is {}face".format(not_text)
    if isinstance(prog, IsText):
        return "is {}text".format(not_text)
    if isinstance(prog, GetFace):
        return "is {}face with id ".format(not_text) + str(prog.index)
    if isinstance(prog, IsObject):
        return "is {}".format(not_text) + prog.obj
    if isinstance(prog, MatchesWord):
        return "is {}text matching term '{}'".format(not_text, prog.word)
    if isinstance(prog, IsPhoneNumber):
        return "is {}phone number".format(not_text)
    if isinstance(prog, IsPrice):
        return "is {}price".format(not_text)
    if isinstance(prog, IsSmiling):
        return "is {}smiling face".format(not_text)
    if isinstance(prog, EyesOpen):
        return "is {}face with eyes open".format(not_text)
    if isinstance(prog, MouthOpen):
        return "is {}face with mouth open".format(not_text)
    if isinstance(prog, AboveAge):
        return "is {}above age ".format(not_text) + str(prog.age)
    if isinstance(prog, BelowAge):
        return "is {}below age ".format(not_text) + str(prog.age)
    if isinstance(prog, Complement):
        return get_nl_explanation(prog.extractor, not not_text)
    if isinstance(prog, Map):
        position_to_str = {
            'GetLeft': 'is left of ',
            'GetRight': 'is right of ',
            'GetNext': 'is left of ',
            'GetPrev': 'is right of ',
            'GetBelow': 'is below ',
            'GetAbove': 'is above ',
            'GetContains': 'is contained in ',
            'GetIsContained': 'contains ',
        }
        position_str = position_to_str[str(prog.position)]
        sub_expl1 = get_nl_explanation(prog.restriction)
        sub_expl2 = get_nl_explanation(prog.extractor)
        expl = sub_expl1 + " that " + position_str + "an object that " + sub_expl2
        if neg:
            expl = expl[:2] + " not" + expl[2:]
        return expl


if __name__ == "__main__":
    app.run(debug=True)

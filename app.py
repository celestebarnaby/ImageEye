from flask import Flask, request, jsonify
from utils import *
from synthesizer import *
app = Flask(__name__)

img_to_environment = {}

@app.route("/data")
def hello():
    global img_to_environment
    img_to_environment = preprocess("react-todo-app/src/components/ui/images/", 100)
    return {
        'message': img_to_environment
    }

@app.route("/loadFiles", methods=['POST'])
def load_files():
    global img_to_environment
    data = request.get_json()
    img_to_environment = preprocess("react-todo-app/src/components/ui/images/" + data + "/", 100)
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
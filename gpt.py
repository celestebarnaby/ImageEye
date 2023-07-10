import openai
import random
import copy
import time
from new_interpreter import *
from utils import *
from new_dsl import *
from new_synthesizer import *
import regex as re

with open("../gpt-key.txt") as f:
    sk = f.read().strip()

openai.api_key = sk


class Hole:
    def __init__(self, node_type, val=None):
        self.node_type = node_type
        self.val = None

    def __str__(self):
        return type(self).__name__

    def duplicate(self):
        return Hole(self.node_type)

    def __lt__(self, other):
        if not isinstance(other, Hole):
            return False
        return str(self) < str(other)


class Tree:
    def __init__(self):
        # self.id: int = _id
        self.nodes: Dict[int, Extractor] = {}
        self.to_children: Dict[int, List[int]] = {}
        self.to_parent: Dict[int, int] = {}
        # self.node_id_counter = itertools.count(0)
        # self.depth = 1
        # self.size = 1
        self.var_nodes = []

    def duplicate(self) -> "Tree":
        ret = Tree()
        # ret.nodes = copy.copy(self.nodes)
        ret.nodes = {}
        for key, val in self.nodes.items():
            if isinstance(val, Hole) or isinstance(val, Node):
                ret.nodes[key] = val.duplicate()
            else:
                ret.nodes[key] = val
        ret.to_children = self.to_children.copy()
        ret.to_parent = self.to_parent.copy()
        # ret.node_id_counter = itertools.tee(self.node_id_counter)[1]
        ret.var_nodes = self.var_nodes.copy()
        # ret.depth = self.depth
        # ret.size = self.size
        return ret

    def __lt__(self, other):
        if self.size == other.size and self.depth == other.depth:
            return self.id < other.id
        if self.size == other.size:
            return self.depth < other.depth
        return self.size < other.size


class Benchmark:
    def __init__(self, gt_prog, desc, dataset_name, example_imgs=[]):
        self.gt_prog = gt_prog
        self.desc = desc
        self.dataset_name = dataset_name
        self.ast_depth = get_ast_depth(gt_prog)
        self.ast_size = get_ast_size(gt_prog)
        self.example_imgs = example_imgs


def get_ast_depth(prog):
    if isinstance(prog, Union) or isinstance(prog, Intersection):
        return max([get_ast_depth(extr) for extr in prog.extractors]) + 1
    if isinstance(prog, Complement) or isinstance(prog, Map):
        return get_ast_depth(prog.extractor) + 1
    if (
        isinstance(prog, IsFace)
        or isinstance(prog, IsText)
        or isinstance(prog, IsPhoneNumber)
        or isinstance(prog, IsPrice)
        or isinstance(prog, IsSmiling)
        or isinstance(prog, EyesOpen)
        or isinstance(prog, MouthOpen)
    ):
        return 2
    else:
        return 3


def get_ast_size(prog):
    if isinstance(prog, Union) or isinstance(prog, Intersection):
        return sum([get_ast_size(extr) for extr in prog.extractors]) + 1
    if isinstance(prog, Complement):
        return get_ast_size(prog.extractor) + 1
    if isinstance(prog, Map):
        if isinstance(prog.position, GetIsContained):
            extra_size = 1
        else:
            extra_size = 2
        return (
            get_ast_size(prog.extractor)
            + get_ast_size(prog.restriction)
            + extra_size
            - 1
        )
    if (
        isinstance(prog, IsFace)
        or isinstance(prog, IsText)
        or isinstance(prog, IsPhoneNumber)
        or isinstance(prog, IsPrice)
        or isinstance(prog, IsSmiling)
        or isinstance(prog, EyesOpen)
        or isinstance(prog, MouthOpen)
    ):
        return 2
    else:
        return 3


easy_benchmarks = [
    Benchmark(IsFace(), "A face", "cars"),
    Benchmark(IsSmiling(), "A smiling face", "wedding"),
    Benchmark(GetFace(8), "Face with id 8", "wedding"),
    Benchmark(IsObject("Car"), "A car", "cars"),
    Benchmark(IsObject("Bicycle"), "A bicycle", "cars"),
    Benchmark(BelowAge(18), "A face that is younger than 18", "wedding"),
]

benchmarks = [
    Benchmark(
        Map(GetFace(8), IsFace(), GetNext()),
        "Face to the right of the face with ID 8.",
        "wedding",
        [
            "Ana Maria Photography-105.jpg",
            "Ana Maria Photography-18.jpg",
            "Ana Maria Photography-42.jpg",
            "Ana Maria Photography-49.jpg",
            "Ana Maria Photography-102.jpg",
        ],
    ),
    Benchmark(
        Map(IsFace(), IsFace(), GetAbove()),
        "Face that is behind another face.",
        "wedding",
        [
            "Ana Maria Photography-100.jpg",
            "Ana Maria Photography-101.jpg",
            "Ana Maria Photography-53.jpg",
            "Ana Maria Photography-49.jpg",
            "Ana Maria Photography-102.jpg",
        ],
    ),
    Benchmark(
        Intersection([Complement(IsSmiling()), Map(IsFace(), IsFace(), GetAbove())]),
        "Face that is behind another face, and is not smiling.",
        "wedding",
        [
            "Ana Maria Photography-100.jpg",
            "Ana Maria Photography-101.jpg",
            "Ana Maria Photography-53.jpg",
            "Ana Maria Photography-49.jpg",
            "Ana Maria Photography-102.jpg",
        ],
    ),
    Benchmark(
        Intersection(
            [Map(IsFace(), IsFace(), GetNext()), Map(IsFace(), IsFace(), GetPrev())]
        ),
        "Face that is between two other faces",
        "wedding",
        [
            "Ana Maria Photography-68.jpg",
            "Ana Maria Photography-40.jpg",
            "Ana Maria Photography-102.jpg",
            "Ana Maria Photography-53.jpg",
            "Ana Maria Photography-2.jpg",
        ],
    ),
    Benchmark(
        Intersection([IsSmiling(), EyesOpen()]),
        "Face that is smiling and has open eyes",
        "wedding",
        [
            "Ana Maria Photography-80.jpg",
            "Ana Maria Photography-38.jpg",
            "Ana Maria Photography-33.jpg",
            "Ana Maria Photography-49.jpg",
            "Ana Maria Photography-102.jpg",
        ],
    ),
    Benchmark(
        Intersection([IsFace(), Complement(Intersection([IsSmiling(), EyesOpen()]))]),
        "Face that is not smiling and has open eyes",
        "wedding",
        [
            "Ana Maria Photography-102.jpg",
            "Ana Maria Photography-54.jpg",
            "Ana Maria Photography-55.jpg",
            "Ana Maria Photography-33.jpg",
            "Ana Maria Photography-49.jpg",
        ],
    ),
    Benchmark(
        Intersection([IsSmiling(), EyesOpen(), Complement(GetFace(8))]),
        "Face that is not smiling with open eyes, that isn't face 8",
        "wedding",
        [
            "Ana Maria Photography-54.jpg",
            "Ana Maria Photography-68.jpg",
            "Ana Maria Photography-40.jpg",
            "Ana Maria Photography-102.jpg",
            "Ana Maria Photography-33.jpg",
        ],
    ),
    Benchmark(
        Intersection([IsFace(), Complement(GetFace(8))]),
        "Face that is not face with id 8.",
        "wedding",
        [
            "Ana Maria Photography-91.jpg",
            "Ana Maria Photography-122.jpg",
            "Ana Maria Photography-66.jpg",
            "Ana Maria Photography-49.jpg",
            "Ana Maria Photography-102.jpg",
        ],
    ),
    Benchmark(
        Map(IsObject("Car"), IsFace(), GetContains()),
        "A face inside a car.",
        "cars",
        [
            "7051526761_7f1293207a_k.jpg",
            "7277639906_2f455d0a66_c.jpg",
            "7283056644_e9ca3877d1_c.jpg",
            "15598753673_331ea65b54_c.jpg",
            "44929498572_0b602cb182_c.jpg",
        ],
    ),
    Benchmark(
        Complement(IsObject("Car")),
        "An object that is not a car.",
        "cars",
        [
            "9107010_479657625c_o.jpg",
            "5421932595_68f7ab545d_c.jpg",
            "5648671688_8b85d9af12_c.jpg",
            "6708503525_870ea33fd2_c.jpg",
            "7051526761_7f1293207a_k.jpg",
        ],
    ),
    Benchmark(
        Complement(Union([IsObject("Car"), IsObject("Bicycle")])),
        "An object that is not a car or a bicycle.",
        "cars",
        [
            "38173050612_88886a495d_c.jpg",
            "41195542880_7166141ab7_c.jpg",
            "7283056644_e9ca3877d1_c.jpg",
            "44015278360_ae3fb72419_c.jpg",
            "44929498572_0b602cb182_c.jpg",
        ],
    ),
    Benchmark(
        Map(IsObject("Car"), IsText(), GetContains()),
        "A car with text on it.",
        "cars",
        [
            "7283056644_e9ca3877d1_c.jpg",
            "car1.jpeg",
            "5648671688_8b85d9af12_c.jpg",
            "6708503525_870ea33fd2_c.jpg",
            "7051526761_7f1293207a_k.jpg",
        ],
    ),
    Benchmark(
        Intersection(
            [IsText(), Complement(Map(IsObject("Car"), IsText(), GetContains()))]
        ),
        "Text that is not written on a car.",
        "cars",
        [
            "n02958343_1902.JPEG",
            "n02958343_3671.JPEG",
            "n02958343_4294.JPEG",
            "n02958343_4588.JPEG",
            "n02958343_9005.JPEG",
        ],
    ),
    Benchmark(
        Map(IsObject("Person"), IsObject("Bicycle"), GetBelow()),
        "A bicycle that is being ridden",
        "cars",
        [
            "42957663251_025fb32ac8_c.jpg",
            "n02834778_4305.JPEG",
            "n02834778_63.JPEG",
            "n02834778_1127.JPEG",
            "n02834778_2263.JPEG",
        ],
    ),
    Benchmark(
        Intersection(
            [
                IsObject("Bicycle"),
                Complement(Map(IsObject("Person"), IsObject("Bicycle"), GetBelow())),
            ]
        ),
        "A bicycle that is not being ridden",
        "cars",
        [
            "42957663251_025fb32ac8_c.jpg",
            "14439655154_4598f22beb_c.jpg",
            "n02834778_63.JPEG",
            "n02834778_1127.JPEG",
            "n02834778_2263.JPEG",
        ],
    ),
    Benchmark(
        Intersection(
            [
                IsObject("Bicycle"),
                Complement(Map(BelowAge(18), IsObject("Bicycle"), GetBelow())),
            ]
        ),
        "A bicycle that is not being ridden by a child",
        "cars",
        [
            "42957663251_025fb32ac8_c.jpg",
            "14439655154_4598f22beb_c.jpg",
            "n02834778_1724.JPEG",
            "n02834778_1127.JPEG",
            "n02834778_2263.JPEG",
        ],
    ),
    Benchmark(
        Intersection(
            [IsFace(), Complement(Map(IsObject("Bicycle"), IsFace(), GetAbove()))]
        ),
        "The face of a person who is not on a bicycle",
        "cars",
        [
            "42957663251_025fb32ac8_c.jpg",
            "14439655154_4598f22beb_c.jpg",
            "n02834778_63.JPEG",
            "n02834778_1127.JPEG",
            "n02834778_2263.JPEG",
        ],
    ),
    Benchmark(
        Map(IsObject("Guitar"), IsFace(), GetAbove()),
        "A guitar that is below a face",
        "guitars",
        [
            "35138463884_d6e585ec6f_c.jpg",
            "2559459918_22441e06e6_c.jpg",
            "173177904_4033f5d57a_z.jpg",
            "207443806_9f7c547646_c.jpg",
            "325813428_db3474fe2f_c.jpg",
        ],
    ),
    Benchmark(
        Intersection(
            [IsFace(), Complement(Map(IsObject("Guitar"), IsFace(), GetAbove()))]
        ),
        "A face that is not below a guitar",
        "guitars",
        [
            "6176795637_c6ff252d4a_c.jpg",
            "2729314473_4272a55d86_c.jpg",
            "2982619528_a19341718f_c.jpg",
            "35138463884_d6e585ec6f_c.jpg",
            "325813428_db3474fe2f_c.jpg",
        ],
    ),
]


def clean_img(img):
    for obj in img.values():
        for key in {
            "Prevmost",
            "Nextmost",
            "Leftmost",
            "Rightmost",
            "Topmost",
            "Bottommost",
            "Hash",
            "Emotions",
            "ObjPosInImgLeftToRight",
            "ImgIndex",
        }:
            if key in obj:
                del obj[key]
        obj["Bounding Box"] = {
            "Left": obj["Loc"][0],
            "Right": obj["Loc"][2],
            "Top": obj["Loc"][1],
            "Bottom": obj["Loc"][3],
        }
        del obj["Loc"]
        if "AgeRange" in obj:
            obj["Age"] = obj["AgeRange"]["High"]
            del obj["AgeRange"]
    return list(img.values())


def get_prompts():
    pos_examples = []
    neg_examples = []
    args = get_args()
    while len(pos_examples) < 50 or len(neg_examples) < 50:
        print(len(pos_examples))
        print(len(neg_examples))
        b = random.choice(benchmarks)
        img_folder = "test_images/" + b.dataset_name + "/"
        img_to_environment = preprocess(img_folder, args.max_faces)
        small_img_to_environment = {
            k: v["environment"]
            for (k, v) in img_to_environment.items()
            if len(v["environment"]) <= 15 and len(v["environment"]) > 0
        }
        need_true = random.random()
        # if need_true > 0.75:
        if False:
            has_true = False
            used_imgs = set()
            while not has_true:
                if len(used_imgs) >= len(small_img_to_environment):
                    rand_img = None
                    break
                rand_img = random.choice(
                    list(set(small_img_to_environment.keys()) - used_imgs)
                )
                output = eval_extractor(b.gt_prog, small_img_to_environment[rand_img])
                if len(output) > 0:
                    has_true = True
                else:
                    used_imgs.add(rand_img)
        else:
            rand_img = random.choice(list(small_img_to_environment.keys()))
            print(small_img_to_environment[rand_img])
            output = eval_extractor(b.gt_prog, small_img_to_environment[rand_img])
        if rand_img:
            img_rep = clean_img(copy.deepcopy(small_img_to_environment[rand_img]))
            if len(output) > 0:
                pos_examples.append((img_rep, True, rand_img, b.desc))
            else:
                neg_examples.append((img_rep, False, rand_img, b.desc))
    return pos_examples[:50], neg_examples[:50]


def make_gpt_queries(intro_text, examples, queries):
    # messages = []
    results = []
    # messages.append({"role": "system", "content": intro_text})
    message = intro_text
    for example, res, _, desc in examples:
        example_content = "image: {}\nproperty: {}\n".format(example, desc)
        message += example_content
        message += "output: {}\n\n".format(str(res))
        # messages.append({"role": "user", "content": content})
        # messages.append({"role": "assistant", "content": str(res)})
    for i, (query, res, _, desc) in enumerate(queries):
        if i % 5 == 0:
            print(i)
            time.sleep(1)
        query_content = "image: {}\nproperty: {}\noutput: ".format(query, desc).replace(
            "'", ""
        )
        # message += query_content
        # content = content.replace("'", "")
        # query_msg = {"role": "user", "content": content}
        # output = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo", temperature=0, messages=messages + [query_msg]
        # )
        # print("MESSAGE")
        # print(message)
        message = message.replace("'", "")
        output = openai.Completion.create(
            model="text-davinci-003", temperature=0, prompt=message + query_content
        )
        # results.append((output["choices"][0]["message"]["content"], str(res)))
        results.append((output["choices"][0]["text"].strip(), str(res)))
    return results


def gtp_experiment1():
    pos_examples, neg_examples = get_prompts()
    examples = [example for example in pos_examples[:3]] + [
        example for example in neg_examples[:3]
    ]
    queries = [example for example in pos_examples[2:]] + [
        example for example in neg_examples[2:]
    ]
    random.shuffle(examples)
    random.shuffle(queries)
    intro_text = "You will be given a list of objects in an image. Each object is represented by a mapping from its properties to its values. The bounding box defines the coordinates of the object in the image. You will also be given a property. I want you to identify if that image has that property. You should be able to determine if an image has a property based on the list of objects. For instance, you can tell if object A is to the right of object B by checking whether the 'Right' coordinate of object A is greater than the 'Right' coordinate of object B. Answer with just True or False. Here are some examples:\n"
    results = None
    while not results:
        # try:
        results = make_gpt_queries(intro_text, examples, queries)
        # except Exception:
        # print("GPT failed")
        # time.sleep(10)
        # continue
    print(results)
    rows = [
        (
            "Query",
            "Image",
            "Image repr",
            "GPT Output",
            "Ground Truth",
            "Correct prediction?",
            "# objects in image",
        )
    ]
    for (output, actual), (img_rep, _, query, image) in zip(results, queries):
        rows.append(
            (
                query,
                image,
                img_rep,
                output,
                actual,
                output == actual
                or (actual == "False" and output.startswith("Cannot determine")),
                len(img_rep),
            )
        )
    num_correct_outputs = len([row for row in rows if row[5]])
    num_false_positives = len(
        [row for row in rows if row[3] == "True" and row[4] == "False"]
    )
    num_false_negatives = len(
        [row for row in rows if row[3] == "False" and row[4] == "True"]
    )
    print("\% Correct: {}".format(num_correct_outputs / len(rows)))
    print("\% False Positives: {}".format(num_false_positives / len(rows)))
    print("\% False Negatives: {}".format(num_false_negatives / len(rows)))
    name = "gpt_output.csv"
    with open(name, "w") as f:
        fw = csv.writer(f)
        for row in rows:
            fw.writerow(row)


def make_text_query(query, env, examples):
    example_progs = [
        (
            "Every person is next to a cat",
            "ForAll x.(Exists y.((Is(y, cat)) And ((Is(x, person)) -> (IsNextTo(x, y)))))",
        ),
        (
            "The image contains a face that is smiling, and has their eyes open",
            "Exists x.((Is(x, smilingFace)) And (Is(x, eyesOpenFace)))",
        ),
        (
            "Alice is in the image and everyone is smiling",
            "Exists x.(ForAll y.((Is(x, Alice)) And ((Is(y, face)) -> (Is(y, smilingFace)))))",
        ),
        # (
        #     "The image contains a face that is not smiling",
        #     "Exists x.((Is(x, face)) And (Not (Is(x, smilingFace))))",
        # ),
        # (
        #     "Every bicycle in the image is being ridden by a person",
        #     "ForAll x.(Exists y.((Is(y, person)) And (Is(x, bicycle)) -> (IsAbove(y, x))))",
        # ),
        (
            "The image contains a cat inside a box.",
            "Exists x.(Exists y.((Is(y, cat) And ((Is(x, box)) And (IsInside(y, x))))))",
        ),
        # (
        #     "Alice is to the right of Bob",
        #     "Exists x.((Is(x, Alice)) And (IsRight(x, Bob)))",
        # ),
        ("There is a tree in the image.", "Exists x.(Is(x, Tree))"),
        (
            "The image contains a chair and a table",
            "Exists x.(Exists y.((Is(x, chair)) And (Is(y, table))))",
        ),
        # (
        #     "Alice and Bob are next to each other",
        #     "Exists x.((Is(x, Alice)) And (IsNextTo(x, Bob)))",
        # ),
        (
            "All faces are not smiling",
            "ForAll x.((Is(x, face)) -> (Not (Is(x, smilingFace))))",
        ),
    ]
    message_text = ""
    for prog in example_progs:
        message_text += "task: {}\nprogram:{}\n\n".format(prog[0], prog[1])
    query_content = "task: {}\nprogram: ".format(query)
    message = {"role": "system", "content": message_text + query_content}
    output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", temperature=0.8, messages=[message], n=5
    )
    objects = get_objects(env)
    # output_trees = [
    #     parse_formula2(choice["message"]["content"].strip(), Tree(), objects)
    #     for choice in output["choices"]
    # ]
    output_trees = []
    for choice in output["choices"]:
        tree = Tree()
        if parse_formula2(choice["message"]["content"].strip(), tree, objects):
            output_trees.append(tree)
    print([choice["message"]["content"] for choice in output["choices"]])
    # print(output_trees)
    # print('hihi')
    # output_trees = list(filter(lambda x: x is not None, output_trees))

    output_progs = [
        fill_in_holes(tree, examples, env, objects)
        if len(tree.var_nodes) > 0
        else construct_prog_from_tree(tree)
        for tree in output_trees
    ]

    # output_progs = [construct_prog_from_tree(tree) for tree in output_trees]
    # print([str(prog) for prog in output_progs])
    # print()

    # output_progs = [
    #     fill_in_holes(tree, examples, env, objects)
    #     if len(tree.var_nodes) > 0
    #     else construct_prog_from_tree(tree)
    #     for tree in output_trees
    # ]
    # print([str(prog) for prog in output_progs])
    # raise TypeError
    if examples:
        progs_matching_examples = []
        for prog in output_progs:
            matching = True
            for img, output in examples:
                if eval_prog(prog, env[img]["environment"]) != output:
                    matching = False
                    break
            if matching:
                progs_matching_examples.append(prog)
    else:
        progs_matching_examples = output_progs
    if not progs_matching_examples:
        return [], str([choice["message"]["content"] for choice in output["choices"]])
    top_prog = progs_matching_examples[0]
    matching_imgs = []
    print(top_prog)
    for img, img_env in env.items():
        if eval_prog(top_prog, img_env["environment"]):
            matching_imgs.append(img)
    print(len(matching_imgs))
    return matching_imgs, str(top_prog)


def gpt_experiment2():
    #     intro_text = """
    # Given an image search task, translate the task into a formula in first order logic. A formula is defined inductively as follows:
    # - Given terms t1, t2, Is(t1, t2) is a formula.
    # - Given terms t1, t2, IsAbove(t1, t2), IsLeft(t1, t2), IsInside(t1, t2), and IsNextTo(t1, t2) are formulas.
    # - For each formula F, Not F is a formula.
    # - For each pair of formulas F, G, (F And G) and (F -> G) are formulas.
    # - If F is a formula and x is a variable, then Exists x.F and ForAll x.F are formulas.\n
    #     """
    intro_text = ""
    progs = [
        (
            "Every person in the image is riding a bicycle",
            "ForAll x.((Is(x, person)) -> (IsAbove(x, bicycle)))",
        ),
        (
            "The image contains a face that is smiling, and has their eyes open",
            "Exists x.((Is(x, smilingFace)) And (Is(x, eyesOpenFace)))",
        ),
        (
            "Alice is in the image and everyone is smiling",
            "Exists x.(ForAll y.((Is(x, Alice)) And ((Is(y, face)) -> (Is(y, smilingFace)))))",
        ),
        (
            "The image contains a face that is not smiling",
            "Exists x.((Is(x, face)) And (Not (Is(x, smilingFace))))",
        ),
        (
            "Every bicycle in the image is being ridden by a person",
            "ForAll x.((Is(x, bicycle)) -> (IsAbove(person, x)))",
        ),
        (
            "The image contains a car with a person inside",
            "Exists x.((Is(x, car)) And (IsInside(x, person)))",
        ),
        (
            "In the image, Alice is to the right of Bob",
            "Exists x.((Is(x, Alice)) And (IsRight(x, Bob)))",
        ),
        ("Alice is in the image", "Exists x.(Is(x, Alice))"),
        (
            "The image contains Alice and Bob",
            "Exists x.(Exists y.((Is(x, Alice)) And (Is(y, Bob))))",
        ),
        (
            "Alice and Bob are next to each other",
            "Exists x.((Is(x, Alice)) And (IsNextTo(x, Bob)))",
        ),
        (
            "All faces are not smiling",
            "ForAll x.((Is(x, face)) -> (Not (Is(x, smilingFace))))",
        ),
    ]
    message_text = intro_text
    # random.shuffle(progs)
    rows = [("Task", "GT Program", "Output Program")]
    for prog in progs[:4]:
        print(prog)
        message_text += "task: {}\nprogram:{}\n\n".format(prog[0], prog[1])
    for prog in progs[4:]:
        query_content = "task: {}\nprogram: ".format(prog[0])
        message = {"role": "system", "content": message_text + query_content}
        print(message)
        output = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", temperature=0.8, messages=[message], n=5
        )
        print(output)
        rows.append(
            (
                prog[0],
                prog[1],
                [output["choices"][i]["message"]["content"].strip() for i in range(5)],
            )
        )
    name = "gpt_output2.csv"
    with open(name, "w") as f:
        fw = csv.writer(f)
        for row in rows:
            fw.writerow(row)


def parse_formula(formula):
    formulas = [
        ("^ForAll (\w*).\((.*)\)$", ForAll),
        ("^Exists (\w*).\((.*)\)$", Exists),
    ]
    one_param_subformulas = [
        ("^Not \((.*)\)$", Not),
    ]
    two_param_subformulas = [
        ("(?<=^\((.*)\)) -> (?=\((.*)\)$)", IfThen),
        ("(?<=^\((.*)\)) And (?=\((.*)\)$)", And),
    ]
    predicates = [
        ("^Is\((\w*), (\w*)\)$", Is),
        ("^IsAbove\((\w*), (\w*)\)$", IsAbove),
        ("^IsLeft\((\w*), (\w*)\)$", IsLeft),
        ("^IsNextTo\((\w*), (\w*)\)$", IsNextTo),
        ("^IsInside\((\w*), (\w*)\)$", IsInside),
    ]
    for regex, f in formulas:
        m = re.search(regex, formula)
        if m is not None:
            var = m.group(1)
            subformula = m.group(2)
            parsed_subformula = parse_formula(subformula)
            if parsed_subformula is not None:
                return f(var, parsed_subformula)
    for regex, f in one_param_subformulas:
        m = re.search(regex, formula)
        if m is not None:
            subformula = m.group(1)
            parsed_subformula = parse_formula(subformula)
            if parsed_subformula is not None:
                return f(parsed_subformula)
    for regex, f in two_param_subformulas:
        m = re.findall(regex, formula)
        for subformula1, subformula2 in m:
            parsed_subformula1, parsed_subformula2 = parse_formula(
                subformula1
            ), parse_formula(subformula2)
            if parsed_subformula1 is not None and parsed_subformula2 is not None:
                return f(parsed_subformula1, parsed_subformula2)
    for regex, f in predicates:
        m = re.search(regex, formula)
        if m is not None:
            var1, var2 = m.group(1), m.group(2)
            return f(var1, var2)
    return None


str_to_pred = {
    "Is": Is,
    "IsAbove": IsAbove,
    "IsLeft": IsLeft,
    "IsNextTo": IsNextTo,
    "IsInside": IsInside,
}


def parse_formula2(formula, tree, objects, parent_node_num=None, used_vars=[]):
    formulas = [
        ("^ForAll (\w*).\((.*)\)$", ForAll),
        ("^Exists (\w*).\((.*)\)$", Exists),
    ]
    one_param_subformulas = [
        ("^Not \((.*)\)$", Not),
    ]
    two_param_subformulas = [
        ("(?<=^\((.*)\)) -> (?=\((.*)\)$)", IfThen),
        ("(?<=^\((.*)\)) And (?=\((.*)\)$)", And),
    ]
    predicate = "^(Is\w*)\((\w*), (\w*)\)$"
    new_node_num = len(tree.nodes)
    for regex, f in formulas:
        m = re.search(regex, formula)
        if m is not None:
            var = m.group(1)
            used_vars.append(var)
            subformula = m.group(2)
            new_node = f(var, None)
            tree.nodes[new_node_num] = new_node
            tree.to_children[new_node_num] = []
            successful_parse = parse_formula2(
                subformula, tree, objects, new_node_num, used_vars
            )
            if successful_parse:
                if parent_node_num is not None:
                    tree.to_parent[new_node_num] = parent_node_num
                    tree.to_children[parent_node_num].append(new_node_num)
                return True
    for regex, f in one_param_subformulas:
        m = re.search(regex, formula)
        if m is not None:
            subformula = m.group(1)
            new_node = f(None)
            tree.nodes[new_node_num] = new_node
            tree.to_children[new_node_num] = []
            successful_parse = parse_formula2(
                subformula, tree, objects, new_node_num, used_vars
            )
            if successful_parse:
                if parent_node_num is not None:
                    tree.to_parent[new_node_num] = parent_node_num
                    tree.to_children[parent_node_num].append(new_node_num)
                return True
    for regex, f in two_param_subformulas:
        m = re.findall(regex, formula)
        for subformula1, subformula2 in m:
            new_node = f(None, None)
            tree.nodes[new_node_num] = new_node
            tree.to_children[new_node_num] = []
            successful_parse1, successful_parse2 = parse_formula2(
                subformula1, tree, objects, new_node_num, used_vars
            ), parse_formula2(subformula2, tree, objects, new_node_num, used_vars)
            if successful_parse1 and successful_parse2:
                if parent_node_num is not None:
                    tree.to_parent[new_node_num] = parent_node_num
                    tree.to_children[parent_node_num].append(new_node_num)
                return True
    m = re.search(predicate, formula)
    if m is not None:
        pred_str = m.group(1)
        var1, var2 = m.group(2), m.group(3)
        if pred_str in str_to_pred:
            f = str_to_pred[pred_str]
            new_node = f(var1, var2)
        else:
            new_node = Hole("relation")
            tree.var_nodes.append(new_node_num)
        # new_node = f(var1, var2)
        tree.nodes[new_node_num] = new_node
        tree.to_children[new_node_num] = []
        for var in [var1, var2]:
            new_child_node_num = len(tree.nodes)
            if var in used_vars or var in objects:
                new_child_node = var
            else:
                new_child_node = Hole("var")
                tree.var_nodes.append(new_child_node_num)
            tree.nodes[new_child_node_num] = new_child_node
            tree.to_children[new_node_num].append(new_child_node_num)
            tree.to_parent[new_child_node_num] = new_node_num
        if parent_node_num is not None:
            tree.to_parent[new_node_num] = parent_node_num
            tree.to_children[parent_node_num].append(new_node_num)
        return True
    return False


def test_parser():
    tests = [
        (
            "Exists x.(Exists y.((Is(y, cat)) And ((Is(x, box)) And (IsInside(y, x)))))",
            Exists(
                "x",
                Exists(
                    "y", And(Is("y", "cat"), And(Is("x", "box"), IsInside("y", "x")))
                ),
            ),
            ["cat", "box"],
        ),
        (
            "ForAll x.((Is(x, person)) -> (IsAbove(x, bicycle)))",
            ForAll("x", IfThen(Is("x", "person"), IsAbove("x", "bicycle"))),
            ["person", "bicycle"],
        ),
        (
            "ForAll x.((Is(x, person)) -> (IsAbove(x, bike)))",
            ForAll("x", IfThen(Is("x", "person"), IsAbove("x", Hole("var")))),
            ["person", "bicycle"],
        ),
        (
            "Exists x.((Is(x, smilingFace)) And (Is(x, eyesOpenFace)))",
            Exists("x", And(Is("x", "smilingFace"), Is("x", "eyesOpenFace"))),
            ["smilingFace", "eyesOpenFace"],
        ),
        (
            "Exists x.(ForAll y.((Is(x, Alice)) And ((Is(y, face)) -> (Is(y, smilingFace)))))",
            Exists(
                "x",
                ForAll(
                    "y",
                    And(
                        Is("x", "Alice"),
                        IfThen(Is("y", "face"), Is("y", "smilingFace")),
                    ),
                ),
            ),
            ["Alice", "face", "smilingFace"],
        ),
        (
            "Exists x.((Is(x, face)) And (Not (Is(x, smilingFace))))",
            Exists("x", And(Is("x", "face"), Not(Is("x", "smilingFace")))),
            ["face", "smilingFace"],
        ),
        (
            "ForAll x.((Is(x, bicycle)) -> (IsAbove(person, x)))",
            ForAll("x", IfThen(Is("x", "bicycle"), IsAbove("person", "x"))),
            ["bicycle", "person"],
        ),
        (
            "ForAll x.((Is(x, bicycle)) -> (IsRiding(person, x)))",
            ForAll("x", IfThen(Is("x", "bicycle"), Hole("relation"))),
            ["bicycle", "person"],
        ),
        (
            "Exists x.((Is(x, car)) And (IsInside(x, person)))",
            Exists("x", And(Is("x", "car"), IsInside("x", "person"))),
            ["car", "person"],
        ),
        (
            "Exists x.((Is(x, Alice)) And (IsLeft(Bob, x)))",
            Exists("x", And(Is("x", Hole("var")), IsLeft(Hole("var"), "x"))),
            [],
        ),
        ("Exists x.(Is(x, Alice))", Exists("x", Is("x", "Alice")), ["Alice"]),
        (
            "Exists x.(Exists y.((Is(x, Alice)) And (Is(y, Bob))))",
            Exists("x", Exists("y", And(Is("x", "Alice"), Is("y", "Bob")))),
            ["Alice", "Bob"],
        ),
        (
            "Exists x.((Is(x, Alice)) And (IsNextTo(x, Bob)))",
            Exists("x", And(Is("x", "Alice"), IsNextTo("x", "Bob"))),
            ["Alice", "Bob"],
        ),
        (
            "ForAll x.((Is(x, face)) -> (Not (Is(x, smilingFace))))",
            ForAll("x", IfThen(Is("x", "face"), Not(Is("x", "smilingFace")))),
            ["face", "smilingFace"],
        ),
    ]
    for test in tests:
        tree = Tree()
        parse_formula2(test[0], tree, test[2], None)
        prog = construct_prog_from_tree(tree)
        if str(prog) != str(test[1]):
            print("FAIL")
            print(test[0])
            print(str(prog))
            print(str(test[1]))
            print()


def test_synthesizer():
    tests = [
        (
            "Exists x.(Exists y.((Is(x, car)) And ((Is(y, person)) And (IsInside(y, x)))))",
            "objects",
            [
                (
                    "image-eye-web/public/images/objects/5421932595_68f7ab545d_c.jpg",
                    True,
                ),
                (
                    "image-eye-web/public/images/objects/3000363792_ded885dd2f_c.jpg",
                    False,
                ),
            ],
        ),
        (
            "Exists x.(Exists y.((Is(x, person)) And ((Is(y, bicycle)) And (IsRiding(x, y)))))",
            "objects",
            [
                ("image-eye-web/public/images/objects/9107010_479657625c_o.jpg", True),
                (
                    "image-eye-web/public/images/objects/3000363792_ded885dd2f_c.jpg",
                    False,
                ),
            ],
        ),
    ]
    for test in tests:
        tree = Tree()
        res = parse_formula2(test[0], tree, ["person", "bicycle"])
        if not res:
            print("PARSING FAILED")
            raise TypeError
        img_folder = "image-eye-web/public/images/" + test[1] + "/"
        img_to_env, _ = preprocess(img_folder)
        examples = test[2]
        prog = fill_in_holes(tree, examples, img_to_env, get_objects(img_to_env))
        print(prog)


if __name__ == "__main__":
    # gpt_experiment2()
    # test_parser()
    test_synthesizer()

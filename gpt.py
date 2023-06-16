import openai
import random
import copy
import time
from interpreter import *
from utils import *
from dsl import *

with open("../gpt-key.txt") as f:
    sk = f.read().strip()

openai.api_key = sk


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


def gpt_experiment2():
    intro_text = """
Given an image search task, translate the task into a program in the following programming language:

P := Exists(E) | All(E_1, E_2) | And(P_1, ..., P_n)
E := Is(\phi) | Complement(E) | Intersect(E_1, ..., E_n) | HasRelation(E_1, E_2, R)
R := IsAbove, IsLeft, IsNextTo, Contains

phi is a predicate that can be equal to any term in the search query. An All program means for every object matching E_1, E_2 is true. \n
    """
    progs = [
        (
            "Every person is riding a bicycle",
            "All(IsObject(person), HasRelation(IsObject(person), IsObject(bicycle), IsAbove))",
        ),
        (
            "Every bicycle is being ridden by a person",
            "All(IsObject(bicycle), HasRelation(IsObject(person), IsObject(bicycle), IsAbove))",
        ),
        (
            "a car with a person inside",
            "Exists(HasRelation(IsObject(car), IsObject(person), Contains))",
        ),
        (
            "a face that is not smiling",
            "Exists(Intersection(IsObject(Face), Complement(IsObject(SmilingFace))",
        ),
        (
            "Alice is to the right of Bob",
            "Exists(HasRelation(IsObject(Alice), IsObject(Bob), IsLeft))",
        ),
        ("Alice is there", "Exists(IsObject(Alice))"),
        (
            "A face that is smiling, and has their eyes open",
            "Exists(Intersection(IsObject(SmilingFace), IsObject(EyesOpenFace)))",
        ),
        ("Alice and Bob", "And(Exists(IsObject(Alice)), Exists(IsObject(Bob)))"),
        (
            "Alice and Bob are next to each other",
            "Exists(HasRelation(IsObject(Alice), IsObject(Bob), NextTo))",
        ),
        (
            "Alice is there and everyone is smiling",
            "And(Exists(IsObject(Alice)), All(IsObject(Face), IsObject(SmilingFace)))",
        ),
        (
            "All faces are not smiling",
            "All(IsObject(face), Intersection(IsObject(Face), Complement(IsObject(SmilingFace)))",
        ),
    ]
    message_text = intro_text
    random.shuffle(progs)
    rows = [("Task", "GT Program", "Output Program")]
    for prog in progs[:3]:
        print(prog)
        message_text += "task: {}\nprogram:{}\n\n".format(prog[0], prog[1])
    for prog in progs[3:]:
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


if __name__ == "__main__":
    gpt_experiment2()

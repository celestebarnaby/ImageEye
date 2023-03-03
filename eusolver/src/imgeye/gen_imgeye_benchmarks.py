import sys

sys.path.append('../../../../ImageEye')

import os
from dsl import *
from benchmarks import benchmarks
from run_imgeye_benchmarks import test_make_solver2
import cProfile
import time
import signal
import io
import pstats
import argparse
import itertools
import random
# from eval_rekognition import eval_extractor
from interpreter import eval_extractor
import csv
import boto3
import cv2
import re
import json


DETAIL_KEYS = [
    # "Eyeglasses",
    # "Sunglasses",
    # "Beard",
    # "Mustache",
    "EyesOpen",
    "Smile",
    "MouthOpen",
    # "AgeRange",
    "IsPrice",
    "IsPhoneNumber"
]

# Since we don't construct class here, some static variables to track things
face_hash_to_id: Dict[str, int] = {}
face_id_to_hash: Dict[int, str] = {}


def add_face_hash_id_mapping(hash_code: str, face_id: int):
    global face_id_to_hash
    global face_hash_to_id


def get_loc(img, bounding_box):
    img_height, img_width = img.shape[0], img.shape[1]
    left = int(bounding_box["Left"] * img_width)
    top = int(bounding_box["Top"] * img_height)
    right = int(left + (bounding_box["Width"] * img_width))
    bottom = int(top + (bounding_box["Height"] * img_height))
    return (left, top, right, bottom)


# Replace face hashes with readable face ids
def clean_environment(img_to_environment):
    new_id = "0"
    for lib in img_to_environment.values():
        new_env = {}
        env = lib["environment"]
        for face_hash, face_details in env.items():
            new_env[new_id] = face_details
            new_id = str(int(new_id) + 1)
        lib["environment"] = new_env


def get_iou(bbox1, bbox2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.
    """
    left1, top1, right1, bottom1 = bbox1
    left2, top2, right2, bottom2 = bbox2

    # determine the coordinates of the intersection rectangle
    int_left = max(left1, left2)
    int_top = max(top1, top2)
    int_right = min(right1, right2)
    int_bottom = min(bottom1, bottom2)

    if int_right < int_left or int_bottom < int_top:
        return 0.0

    # The intersection of two axis-aligned bounding boxes is always an
    # axis-aligned bounding box
    intersection_area = (int_right - int_left) * (int_bottom - int_top)

    # compute the area of both AABBs
    bb1_area = (right1 - left1) * (bottom1 - top1)
    bb2_area = (right2 - left2) * (bottom2 - top2)

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
    assert iou >= 0.0
    assert iou <= 1.0
    return iou


def get_img_score(env, strategy):
    face_set = set()
    if strategy == 1:
        return len(env)
    for details_map in env.values():
        face_str = ""
        for k, v in details_map.items():
            if k not in DETAIL_KEYS or k in {'IsPrice', 'IsPhoneNumber'}:
                continue
            if k == "Emotions":
                for emotion in v:
                    face_str += emotion
            # elif k == 'AgeRange':
            #     face_str += 'Low' + v['Low'] + 'High' + v['High']
            else:
                face_str += k
        face_set.add(face_str)
    if strategy == 2:
        # number of unique faces
        return len(face_set)
    else:
        return len(face_set) / len(env)


def check_regex(text, key):
    regexes = {
        "phone": "^(\\+\\d{1,2}\\s)?\\(?\\d{3}\\)?[\\s.-]?\\d{3}[\\s.-]?\\d{4}$",
        "price": "^\\$?\\d+[.,]\\d{1,2}$",
    }
    return bool(re.match(regexes[key], text))


def is_unique_text_object(bbox_to_text, new_bbox, new_text):
    for bbox, text in bbox_to_text.items():
        if text == new_text:
            if get_iou(bbox, new_bbox) > 0.5:
                return False
    return True


def get_details(
    face_responses,
    text_responses,
    object_responses,
    keys: List[str],
    imgs,
    client,
    img_index,
    prev_environment=None,
    max_faces=10,
) -> Dict[str, Dict[str, Any]]:

    details_list = []
    keys =[
    "Eyeglasses",
    "Sunglasses",
    "Beard",
    "Mustache",
    "EyesOpen",
    "Smile",
    "MouthOpen",
    "AgeRange",
    # "IsPrice",
    # "IsPhoneNumber"
]
    if not prev_environment:
        obj_count = 0
        img_count = 0
    else:
        obj_count = len(prev_environment)
        img_count = max(item["ImgIndex"] for item in prev_environment.values()) + 1
    for img_index, (face_response, text_response, img) in enumerate(zip(face_responses, text_responses, imgs)):
        # print("img_index:", img_index)
        # print('response:', response)
        # print("img:", img)
        faces = face_response["FaceRecords"]
        text_objects = text_response["TextDetections"]
        objects = object_responses[0]["Labels"]
        for face in faces:
            # print("face:", face)
            details = face["FaceDetail"]
            face_hash = face["Face"]["FaceId"]
            details_map = {}
            details_map["Type"] = "Face"
            for key in keys:
                if key == "Emotions":
                    details_map[key] = []
                    emotion_list = details[key]
                    for emotion in emotion_list:
                        if emotion["Confidence"] > 90:
                            details_map[key].append(emotion["Type"])
                elif key == "AgeRange":
                    details_map[key] = details[key]
                else:
                    if details[key]["Value"] and details[key]["Confidence"] > 90:
                        # The value doesn't matter here
                        details_map[key] = True
            # details_map['FacePosInImgLeftToRight'] = i
            details_map["Loc"] = get_loc(img, face["Face"]["BoundingBox"])
            # Check if this face matches another face in the library
            if face_hash in face_hash_to_id:
                face_index = face_hash_to_id[face_hash]
            else:
                # face_index = obj_count
                # add_face_hash_id_mapping(face_id, face_index)
                if prev_environment is None:
                    face_index = obj_count
                else:
                    search_response = client.search_faces(
                        CollectionId="library2", FaceId=face_hash, MaxFaces=max_faces, FaceMatchThreshold=80
                    )
                    hashes_to_indices = {
                        details["Hash"]: details["Index"]
                        for details in prev_environment.values()
                        if details["Type"] == "Face"
                    }
                    matched_face_hashes = [item["Face"]["FaceId"] for item in search_response["FaceMatches"]]
                    face_index = obj_count
                    for matched_face_hash in matched_face_hashes:
                        if matched_face_hash == face_hash:
                            continue
                        if matched_face_hash in hashes_to_indices:
                            face_index = hashes_to_indices[matched_face_hash]
                            break
                        # if matched_face_hash in face_details_maps:
                        #     face_index = face_details_maps[matched_face_id]["Index"]
                        #     break
            details_map["Index"] = face_index
            details_map["Hash"] = face_hash
            details_map["ImgIndex"] = img_index + img_count
            details_list.append(details_map)
            obj_count += 1
        bbox_to_text = {}
        for text_object in text_objects:
            if text_object["Confidence"] < 90:
                continue
            bbox = get_loc(img, text_object["Geometry"]["BoundingBox"])
            if not is_unique_text_object(bbox_to_text, bbox, text_object["DetectedText"]):
                continue
            details_map = {}
            details_map["Type"] = "Text"
            text = text_object["DetectedText"]
            bbox_to_text[bbox] = text
            details_map["Text"] = text
            details_map["Loc"] = bbox
            if check_regex(text, "phone"):
                details_map["IsPhoneNumber"] = True
            if check_regex(text, "price"):
                details_map["IsPrice"] = True
            details_map["Index"] = obj_count
            details_map["ImgIndex"] = img_index + img_count
            details_list.append(details_map)
            obj_count += 1
        for obj in objects:
            # if obj['Name'] not in VALID_LABELS:
            # continue
            for instance in obj["Instances"]:
                if instance["Confidence"] < 90:
                    continue
                details_map = {}
                details_map["Type"] = "Object"
                details_map["Name"] = obj["Name"]
                details_map["Loc"] = get_loc(img, instance["BoundingBox"])
                details_map["Index"] = obj_count
                details_map["ImgIndex"] = img_index + img_count
                details_list.append(details_map)
                obj_count += 1
        details_list.sort(key=lambda d: d["Loc"][0])
        details_maps = {}
        for i, details_map in enumerate(details_list):
            details_map["ObjPosInImgLeftToRight"] = i
            details_maps[i + len(prev_environment)] = details_map

        for target_obj_id, target_details in details_maps.items():
            prev_obj = False
            next_obj = False
            left_obj = False
            right_obj = False
            front_obj = False
            back_obj = False
            target_pos = target_details["ObjPosInImgLeftToRight"]
            target_left, target_top, target_right, target_bottom = target_details["Loc"]
            for obj_id, details in details_maps.items():
                if obj_id == target_obj_id:
                    continue
                pos = details["ObjPosInImgLeftToRight"]
                left, top, right, bottom = details["Loc"]
                if pos < target_pos:
                    prev_obj = True
                else:
                    next_obj = True
                if bottom >= target_top and top <= target_bottom:
                    if left < target_left:
                        left_obj = True
                    else:
                        right_obj = True
                if top < target_top:
                    back_obj = True
                else:
                    front_obj = True
            if not prev_obj:
                target_details["Prevmost"] = True
            if not next_obj:
                target_details["Nextmost"] = True
            if not left_obj:
                target_details["Leftmost"] = True
            if not right_obj:
                target_details["Rightmost"] = True
            if not front_obj:
                target_details["Bottommost"] = True
            if not back_obj:
                target_details["Topmost"] = True

    return details_maps


class IOExample:
    def __init__(
        self,
        trace,
        img_dirs: List[str],
        client,
        gt_prog: str,
        explanation: str,
        max_faces: int,
        prev_env=None,
        img_to_environment=None,
    ):
        self.trace = trace
        self.img_dirs = img_dirs
        self.gt_prog = gt_prog
        self.explanation = explanation
        if img_to_environment:
            env = {}
            for img_dir in img_dirs:
                env = {**env, **img_to_environment[img_dir]["environment"]}
            self.env = env
        else:
            self.env = get_environment1(img_dirs, client, DETAIL_KEYS, prev_env, max_faces)
        for details_map in self.env.values():
            if "ActionApplied" in details_map:
                del details_map["ActionApplied"]
        for action, l in trace.items():
            for (img_index, index) in l:
                for details_map in self.env.values():
                    if details_map["ObjPosInImgLeftToRight"] == index and details_map["ImgIndex"] == img_index:
                        details_map["ActionApplied"] = action
        self.obj_list = self.env.keys()
        # dictionary from action to fta
        self.fta_by_action = {}
        # dictionary from action to state mapping
        self.state_to_forward_transitions_by_action = {}


def get_source_bytes(img: str):
    with open(img, "rb") as source_image:
        source_bytes = source_image.read()
    return source_bytes

def get_client():
    with open("../../../credentials.csv", "r") as _input:
        next(_input)
        reader = csv.reader(_input)
        for line in reader:
            access_key_id = line[2]
            secret_access_key = line[3]

    client = boto3.client(
        "rekognition", aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key, region_name="us-west-2"
    )
    return client


def get_environment1(
    img_dirs: List[str], client, img_index, keys=[], prev_environment=None, max_faces=10
) -> Dict[str, Dict[str, Any]]:
    # The same face in a different photo has a different entry in the library,
    # but the SAME Index
    face_responses = []
    text_responses = []
    object_responses = []
    imgs = []
    for img_dir in img_dirs:
        print("img_dir:", img_dir)
        face_response = client.index_faces(
            CollectionId="library2",
            Image={"Bytes": get_source_bytes(img_dir)},
            MaxFaces=max_faces,
            DetectionAttributes=["ALL"],
        )
        text_response = client.detect_text(Image={"Bytes": get_source_bytes(img_dir)})
        object_response = client.detect_labels(
            Image={"Bytes": get_source_bytes(img_dir)}, MaxLabels=100, MinConfidence=90
        )
        img = cv2.imread(img_dir, 1)
        face_responses.append(face_response)
        text_responses.append(text_response)
        object_responses.append(object_response)
        imgs.append(img)
    return get_details(
        face_responses, text_responses, object_responses, keys, imgs, client, img_index, prev_environment
    )


def preprocess(img_folder, strategy, max_faces=10):
    """
    Given an img_folder, cache all the image's information to a dict, scored by the strategy
    """

    print("loading images and preprocessing...")

    # read the cache if it exists
    key = img_folder + " " + str(strategy) + " " + str(max_faces)
    test_images = {}
    if os.path.exists("../../../test_images.json"):
        with open("../../../test_images.json", "r") as fp:
            test_images = json.load(fp)
            if key in test_images:
                return test_images[key]

    #     cache_dir = '.cache'
    #     cache_file = "{}/{}_{}.pkl".format(cache_dir, img_folder.split('/')[-1], strategy)
    #     if not os.path.exists(cache_dir):
    #         os.mkdir(cache_dir)
    #     else:
    #         if os.path.exists(cache_file):
    #             with open(cache_file, 'rb') as f:
    #                 img_to_environment = pickle.load(f)
    #                 return img_to_environment

    client = get_client()
    client.delete_collection(CollectionId="library2")
    client.create_collection(CollectionId="library2")
    img_to_environment = {}
    prev_env = {}
    img_index = 0

    start_time = time.perf_counter()
    # loop through all image files to cache information
    for filename in os.listdir(img_folder):
        # print("filename:", filename)
        img_dir = img_folder + filename
        env = get_environment1([img_dir], client, img_index, DETAIL_KEYS, prev_env, max_faces)
        # print("environment:", env)
        score = get_img_score(env, strategy)
        # print("score:", score)
        img_to_environment[img_dir] = {"environment": env, "img_index": img_index, "score": score}
        if not env:
            continue
        img_index += 1
        prev_env = prev_env | env
    end_time = time.perf_counter()
    total_time = end_time - start_time

    print("preprocessing finished...")

    clean_environment(img_to_environment)
    print("Num images: ", len(os.listdir(img_folder)))
    print("Total time: ", total_time)
    test_images[key] = img_to_environment
    with open("test_images.json", "w") as fp:
        json.dump(test_images, fp)

    #     # print(env)
    #     print("Num images: ", len(os.listdir(img_folder)))
    #     print("Total time: ", total_time)

    #     # save the cache once finished
    #     with open(cache_file, "wb") as f:
    #         pickle.dump(img_to_environment, f)

    # objects = set()
    # for env in img_to_environment.values():
    #     env = env['environment']
    #     objects.update([details["Name"] for details in env.values() if details["Type"] == "Object"])

    print(img_to_environment)
    # raise TypeError

    return img_to_environment


def get_indices(env, gt_prog):
    """
    Given the ground truth program, and the input image, automatically find out which are the labels by running the program on this input
    """
    ids = eval_extractor(gt_prog, env)
    return [env[obj_id]["ObjPosInImgLeftToRight"] for obj_id in ids]


def get_environment2(client, indices, img_dir, img_to_environment):
    img_index = img_to_environment[img_dir]["img_index"]
    trace = [(img_index, i) for i in indices]
    env = img_to_environment[img_dir]["environment"]
    ex = IOExample(
        {Blur(): trace}, [img_dir], client, "", "", 100, img_to_environment=img_to_environment
    )
    # del img_to_environment[img_dir]
    return env 


def get_differing_images(img_to_environment, prog1, prog2) -> bool:
    """
    Returns the list of images on which 2 programs have different outputs
    """

    print("evaluating program equivalence")
    print("prog1:", prog1)
    print("prog2:", prog2)

    assert len(img_to_environment) > 0
    incorrect_img_ids = []

    for img_id, lib in img_to_environment.items():

        env = lib["environment"]
        ids1 = eval_extractor(prog1, env)
        ids2 = eval_extractor(prog2, env)

        # print("ids1:", ids1)
        # print("ids2:", ids2)

        if ids1 != ids2:
            # print("image id:", img_id)
            # print("ids1:", ids1)
            # print("ids2:", ids2)
            incorrect_img_ids.append(img_id)

    print("Programs differ on " + str(len(incorrect_img_ids)) + " images")
    # print("Incorrect images: ", incorrect_img_ids)
    return incorrect_img_ids


def test_synthesis():
    if not os.path.exists("data"):
        os.mkdir("data")

    client = get_client()
    client.delete_collection(CollectionId="library")
    client.create_collection(CollectionId="library")

    data = []
    pr = cProfile.Profile()
    pr.enable()

    if not os.path.exists("../../benchmarks/imgman"):
        os.mkdir("../../benchmarks/imgman")
    
    benchmark_num = 0 
    text_to_id = {}
    data = []
    overview_data = []
    # with open('example_imgs.json', 'r') as f:
        # benchmark_to_example_imgs = json.load(f)

    for i, benchmark in enumerate(benchmarks):
        print(benchmark.gt_prog)
        annotated_env = {}
        img_folder = "test_images/" + benchmark.dataset_name + "/"
        img_to_environment = preprocess(img_folder, 2, 100)
        prog = benchmark.gt_prog
        # example_imgs = [img_folder + img for img in benchmark.example_imgs]
        example_imgs = []
        img_options = list(img_to_environment.keys())
        rounds = 1
        while rounds <= 10:
            print("Round: ", rounds)
            # example_imgs = [img for img in benchmark_to_example_imgs[str(i)]]
            img_dir, _ = min([(img_dir, img_to_environment[img_dir]["environment"]) for img_dir in img_options], key=lambda tup: (len(tup[1]), str(tup[0])))
            if img_dir in example_imgs:
                img_options.remove(img_dir)
                continue
            example_imgs.append(img_dir)
            for img_dir in example_imgs:
                env = img_to_environment[img_dir]["environment"]
                indices = get_indices(env, prog)
                annotated_env = get_environment2(client, indices, img_dir, img_to_environment) | annotated_env

            if rounds == 1 and not indices:
                img_options.remove(img_dir)
                example_imgs.remove(img_dir)
                annotated_env = {}
                continue
            print("New image: ", img_dir)
            # print(benchmark.gt_prog)
            # print(annotated_env)
            inputs = set()
            outputs = set()
            all_preds = set()
            for obj in annotated_env.values():
                preds = set()
                for key, val in obj.items():
                    if key == 'Type' and val != 'Object':
                        preds.add(key + val)
                    elif key == 'Name':
                        preds.add(key + val)
                    elif key == 'Text':
                        if val in text_to_id:
                            text_id = text_to_id[val]
                        elif not text_to_id:
                            text_id = 0
                            text_to_id[val] = text_id
                        else:
                            text_id = max(text_to_id.values()) + 1
                            text_to_id[val] = text_id
                        preds.add(key + str(text_id))
                    elif key == 'AgeRange':
                        if val['High'] < 18:
                            preds.add('BelowAge18')
                        # elif val['Low'] > 18:
                            # preds.add('AboveAge18')
                    elif key == 'Index' and obj['Type'] == 'Face':
                        preds.add(key + str(val))
                    elif key in DETAIL_KEYS:
                        preds.add(key)
                all_preds.update(preds)
                pred_str = " ".join(preds)
                img_str = "{" + pred_str + " bb: " + str(obj['Loc'][0]) + " " + str(obj['Loc'][2]) + " " + str(obj['Loc'][1]) + " " + str(obj['Loc'][3]) + " " + str(obj['ImgIndex']) + "}"
                inputs.add(img_str)
                if 'ActionApplied' in obj:
                    outputs.add(img_str)
            all_preds_str = "\n\t".join(['"' + pred + '"' for pred in sorted(list(all_preds))])
            input_str = '{' + str(sorted(list(inputs), key=str)).replace("'", "")[1:-1] + '}' #if inputs else "{}"
            output_str = str(outputs).replace("'", "") if outputs else "{}"
            benchmark_str = """
(set-logic IMG)

(synth-fun f ((input Imgs)) Imgs
    ((Start Imgs ((Match input StartStr)
                (Union Start Start)
                (Intersection Start Start)
                (Complement input Start)
                (Find input Start StartStr Pos)
                ))
    (StartStr String (
        {}
        ))
    (Pos String (
        "GetLeft"
        "GetRight"
        "GetAbove"
        "GetBelow"
        "GetParents"
        "GetChildren"
        "GetNext"
        "GetPrev"))))

(declare-var s0 Set)

(constraint (= (f {} ) {} ))

(check-synth)
                """.format(all_preds_str, input_str, output_str)
            benchmark_name = "imgman" + str(benchmark_num) + ".sl"
            filename = '../../benchmarks/imgman/' + benchmark_name
            with open(filename, 'w') as f:
                f.write(benchmark_str)
            id_to_text = {value: key for (key, value) in text_to_id.items()}
            output_prog, total_time = test_make_solver2(filename, id_to_text)
            if output_prog == '(fail)':
                img_options = []
            else:
                img_options = get_differing_images(img_to_environment, output_prog, benchmark.gt_prog)
            row = (
                str(benchmark.gt_prog),
                output_prog,
                benchmark.dataset_name,
                total_time,
                benchmark.desc,
                benchmark.ast_depth,
                benchmark.ast_size,
                len(example_imgs),
                len(annotated_env),
                len(all_preds),
                example_imgs,
            ) 
            overview_data.append(row)
            if not img_options:
                data.append(row)
                print("DONE")
                break
            rounds += 1
            # with open('text_to_id.json', 'w') as f:
            #     json.dump(text_to_id, f)
            # benchmark_num += 1
        if rounds > 10:
            row = (
                str(benchmark.gt_prog),
                "MAX ROUNDS",
                benchmark.dataset_name,
                0,
                benchmark.desc,
                benchmark.ast_depth,
                benchmark.ast_size,
                len(example_imgs),
                len(annotated_env),
                len(all_preds),
                example_imgs,
            )
            overview_data.append(row)
            data.append(row)
    with open('data/results.csv', "w") as f:
        fw = csv.writer(f)
        fw.writerow(
            (
                "Ground Truth Prog",
                "Synthesized Prog",
                "Dataset",
                "Total Time",
                "Description",
                "AST Depth",
                "AST Size",
                "# Example Images",
                "# Objects",
                "# Attributes",
                "Example Images"
            ),
        )
        for row in data:
            fw.writerow(row)
    with open('data/overview.csv', "w") as f:
        fw = csv.writer(f)
        fw.writerow(
            (
                "Ground Truth Prog",
                "Synthesized Prog",
                "Dataset",
                "Total Time",
                "Description",
                "AST Depth",
                "AST Size",
                "# Example Images",
                "# Objects",
                "Example Images"
            ),
        )
        for row in overview_data:
            fw.writerow(row)




if __name__ == "__main__":
    test_synthesis()
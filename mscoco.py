import pylab

# import matplotlib.pyplot as plt
# import skimage.io as io
# import numpy as np
from cocoapi.PythonAPI.pycocotools.coco import COCO
import os
from tqdm import tqdm
import shutil
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2 import model_zoo
import cv2
from detectron2.data import MetadataCatalog
from image_utils import *
import json
import argparse
import pickle

pylab.rcParams["figure.figsize"] = (8.0, 10.0)

dataDir = "../mscoco"
dataType = "val2017"
annFile = "{}/annotations/instances_{}.json".format(dataDir, dataType)

# initialize COCO api for instance annotations
coco = COCO(annFile)

filename_to_id = {img["file_name"]: img["id"] for img in coco.dataset["images"]}

cats = coco.loadCats(coco.getCatIds())
nms = [cat["name"] for cat in cats]
id_to_name = {cat["id"]: cat["name"] for cat in cats}

# display COCO categories and supercategories
# cats = coco.loadCats(coco.getCatIds())
# nms = [cat["name"] for cat in cats]
# id_to_name = {cat["id"]: cat["name"] for cat in cats}
# print(nms)
# print()
# print('COCO categories: \n{}\n'.format(' '.join(nms)))

# nms = set([cat["supercategory"] for cat in cats])
# print('COCO supercategories: \n{}'.format(' '.join(nms)))

# get all images containing given categories, select one at random
# catIds = coco.getCatIds(catNms=["person"])
# imgIds = coco.getImgIds(catIds=catIds)


def get_center(bbox):
    left, top, right, bottom = bbox
    return ((left + right) / 2, (top + bottom) / 2)


def get_mscoco_ground_truth(filename, img_index, num_objects):
    img_id = filename_to_id[filename]
    annIds = coco.getAnnIds(imgIds=img_id)
    anns = coco.loadAnns(annIds)
    env = {}
    for i, ann in enumerate(anns):
        details = {}
        left, top, width, height = ann["bbox"]
        details["Bbox"] = (left, top, left + width, top + height)
        details["Center"] = get_center(ann["bbox"])
        details["Type"] = "Object"
        details["Name"] = id_to_name[ann["category_id"]]
        details["ImgIndex"] = img_index
        env[str(i + num_objects)] = details
    sorted_objs = sorted(env.items(), key=lambda x: x[1]["Center"][0])
    for i, (_, details) in enumerate(sorted_objs):
        details["ObjPosInImgLeftToRight"] = i
    return env


def preprocess_mscoco(img_folder, load_from_cache=True):
    test_images = {}
    if load_from_cache and os.path.exists("mscoco.json"):
        with open("mscoco.json", "r") as fp:
            test_images = json.load(fp)
            if img_folder in test_images:
                return test_images[img_folder]
    img_to_environment = {}
    img_index = 0
    num_objects = 0

    for filename in os.listdir(img_folder):
        img_dir = img_folder + filename
        gt_env = get_mscoco_ground_truth(filename, img_index, num_objects)
        num_objects = num_objects + len(gt_env)
        score = len(gt_env)
        img_to_environment[img_dir] = {
            "ground_truth": gt_env,
            "img_index": img_index,
            # this is used for heuristically selecting examples
            "score": score,
        }
        if not gt_env:
            continue
        img_index += 1
    # do a second pass to generate the environments with predicted labels
    for filename in os.listdir(img_folder):
        img_dir = img_folder + filename
        img_index = img_to_environment[img_dir]["img_index"]
        gt_env = img_to_environment[img_dir]["ground_truth"]
        model_env = get_mscoco_environment(
            img_dir, img_index, num_objects, False, gt_env
        )
        # model_env_with_prediction_sets = get_mscoco_environment(
        # img_dir, img_index, num_objects, True, gt_env
        # )
        num_objects = num_objects + len(model_env)
        img_to_environment[img_dir]["model_env"] = model_env
        # img_to_environment[img_dir]["model_env_with_psets"] = model_env_with_prediction_sets

    test_images[img_folder] = img_to_environment
    with open("test_images.json", "w") as fp:
        json.dump(test_images, fp)

    return img_to_environment


def get_predictor():
    cfg = get_cfg()
    # add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
    cfg.merge_from_file(
        model_zoo.get_config_file("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml")
    )
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
    # Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(
        "COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml"
    )

    metadata = MetadataCatalog.get(cfg.DATASETS.TRAIN[0])
    predictor = DefaultPredictor(cfg)

    return predictor, metadata.get("thing_classes")


# predictor, class_names = get_predictor()


def map_gt_objs_to_preds(env, gt_env):
    """1. maps each ground truth object to list of predicted objects with same label and iou > 0
    2. for each ground truth object, selects matching predicted object with max iou
    3. generates new model environment where obj ids are replaced with matching ids in the gt env (ONLY WHEN there is a matching obj)
    """

    gt_to_preds = {gt_id: [] for gt_id in gt_env.keys()}
    for obj_id, obj in env.items():
        closest_matching_gt_obj = None
        biggest_iou = 0
        for gt_obj_id, gt_obj in gt_env.items():
            iou = get_iou(gt_obj["Bbox"], obj["Bbox"])
            if obj["Name"] != gt_obj["Name"] or iou <= biggest_iou:
                continue
            closest_matching_gt_obj = gt_obj_id
            biggest_iou = iou
        if closest_matching_gt_obj is not None:
            gt_to_preds[closest_matching_gt_obj].append((biggest_iou, obj_id))

    pred_to_gt = {}
    for gt_obj_id, pred_list in gt_to_preds.items():
        if not pred_list:
            continue
        _, matching_pred = max(pred_list)
        pred_to_gt[matching_pred] = gt_obj_id

    new_env = {}
    for obj_id, details in env.items():
        if obj_id in pred_to_gt:
            new_env[pred_to_gt[obj_id]] = details
        else:
            new_env[obj_id] = details
    return new_env

def get_conformal_quantile(score_list, delta):
    calibration_size = len(score_list)
    desired_quantile = np.ceil((1 - delta) * (calibration_size + 1)) / calibration_size
    chosen_quantile = np.minimum(1.0, desired_quantile)
    w = np.quantile(score_list, chosen_quantile)
    return w

def get_confidence_bounds(calib_data, delta):
    lc_score_list = list()
    hic_score_list = list()
    for imgname, img_envs in calib_data.items():
        lc = 2
        hic = -1
        gt_env = img_envs['ground_truth']
        # Assuming the pred_env already has detections mapped to ground truths
        pred_env = img_envs['model_env']
        gt_indices = gt_env.keys()
        for index, obj in pred_env.items():
            if index in gt_indices: # Chosen detection object
                lc = min(obj['ConfidenceScore'], lc)
            else:                   # Not chosen
                hic = max(obj['ConfidenceScore'], hic)
        lc_score_list.append(-1 * lc)
        hic_score_list.append(hic)

    delta_lc = delta / 2 # Determining uncertainty split between two scores - can be hyperparameter 
    delta_hic = delta - delta_lc
    lc_quantile = get_conformal_quantile(lc_score_list, delta_lc)
    corrected_lc_quantile = -1 * lc_quantile
    hic_quantile = get_conformal_quantile(hic_score_list, delta_hic)

    return corrected_lc_quantile, hic_quantile

def get_prediction_set(env, calib_data, delta):
    # Assuming we have calibration data where ground truths are mapped to detections 
    lc, hic = get_confidence_bounds(calib_data, delta)
    pred_set = list()
    for index, obj in env.items():
        if obj['ConfidenceScore'] >= hic: # object is in image
            pred_set.append((obj, 1))
        elif obj['ConfidenceScore'] > lc: # object may or may not be in image
            pred_set.append((obj, 0))
    return pred_set

def get_mscoco_environment(
    filename, img_index, num_objects, use_prediction_sets, gt_env
):
    print(filename)
    im = cv2.imread(filename)
    predictor, class_names = get_predictor()
    outputs = predictor(im)
    bboxes = outputs["instances"].pred_boxes
    scores = outputs["instances"].scores
    classes = [class_names[i] for i in outputs["instances"].pred_classes]
    obj_list = [
        {
            "Name": name.lower(),
            "Bbox": bbox.tolist(),
            "Center": get_center(bbox.tolist()),
            "ConfidenceScore": score.item(),
            "ImgIndex": img_index,
            "Type": "Object",
        }
        for (name, bbox, score) in zip(classes, bboxes, scores)
    ]
    sorted_objs = sorted(obj_list, key=lambda x: x["Center"][0])
    env = {}
    for i, details in enumerate(sorted_objs):
        details["ObjPosInImgLeftToRight"] = i
        env[str(i + num_objects)] = details
    env = map_gt_objs_to_preds(env, gt_env)
    if use_prediction_sets:
        return get_prediction_set(env)
    return env


def check_objects():
    img_folder = "../mscoco/val2017/"
    cats_to_occs = {}
    for filename in tqdm(os.listdir(img_folder)):
        img_dir = img_folder + filename
        img_id = filename_to_id[filename]
        annIds = coco.getAnnIds(imgIds=img_id)
        anns = coco.loadAnns(annIds)
        if len(anns) < 3:
            os.remove(img_dir)
            continue
        for ann in anns:
            name = id_to_name[ann["category_id"]]
            if name not in cats_to_occs:
                cats_to_occs[name] = 0
            cats_to_occs[name] += 1
    sorted_cats_to_occs = {
        k: v
        for k, v in sorted(cats_to_occs.items(), reverse=True, key=lambda item: item[1])
    }
    print(sorted_cats_to_occs)


def make_dataset(dataset_folder):
    multiple_people = 0
    cars_trucks = 0
    person_chair = 0
    dining_table_cup = 0
    traffic_light_car = 0
    car_person = 0
    img_folder = "../mscoco/val2017/"
    new_dataset = set()
    for filename in tqdm(os.listdir(img_folder)):
        img_dir = img_folder + filename
        img_id = filename_to_id[filename]
        annIds = coco.getAnnIds(imgIds=img_id)
        anns = coco.loadAnns(annIds)
        names = [id_to_name[ann["category_id"]] for ann in anns]
        if "car" in names and "truck" in names and cars_trucks < 50:
            new_dataset.add(filename)
            cars_trucks += 1
        elif "person" in names and "chair" in names and person_chair < 50:
            new_dataset.add(filename)
            person_chair += 1
        elif "dining table" in names and "cup" in names and dining_table_cup < 50:
            new_dataset.add(filename)
            dining_table_cup += 1
        elif "traffic light" in names and "car" in names and traffic_light_car < 50:
            new_dataset.add(filename)
            traffic_light_car += 1
        elif "car" in names and "person" in names and car_person < 50:
            new_dataset.add(filename)
            car_person += 1
        elif names.count("person") > 3 and multiple_people < 100:
            new_dataset.add(filename)
            multiple_people += 1
    print("Multiple people: " + str(multiple_people))
    print("Cars and trucks: " + str(cars_trucks))
    print("Person and chair: " + str(person_chair))
    print("Dining table and cup: " + str(dining_table_cup))
    print("Traffic light and car: " + str(traffic_light_car))
    print("Car and person: " + str(car_person))
    print(len(new_dataset))
    if not os.path.isdir(dataset_folder):
        os.mkdir(dataset_folder)
    for filename in new_dataset:
        img_dir = img_folder + filename
        shutil.copyfile(img_dir, dataset_folder + filename)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--make_dataset",
        type=bool,
        default=False,
    )
    parser.add_argument(
        "--preprocess_dataset",
        type=bool,
        default=True,
    )
    parser.add_argument("--dataset_folder", type=str, default="./mscoco_images/")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_args()
    if args.make_dataset:
        make_dataset(args.dataset_folder)
    if args.preprocess_dataset:
        img_to_env = preprocess_mscoco(args.dataset_folder, False)

        # Using data to get lower and upper confidence bounds for object scores 
        lc_quantile, hic_quantile = get_confidence_bounds(img_to_env, 0.1)

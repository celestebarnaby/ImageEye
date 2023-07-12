import pylab
import matplotlib.pyplot as plt
import skimage.io as io
import numpy as np
from cocoapi.PythonAPI.pycocotools.coco import COCO
import os
from tqdm import tqdm
import shutil
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2 import model_zoo
import cv2
from detectron2.data import MetadataCatalog, DatasetCatalog
from image_utils import *

pylab.rcParams["figure.figsize"] = (8.0, 10.0)

dataDir = "../mscoco"
dataType = "val2017"
annFile = "{}/annotations/instances_{}.json".format(dataDir, dataType)

# initialize COCO api for instance annotations
coco = COCO(annFile)

filename_to_id = {img["file_name"]: img["id"] for img in coco.dataset["images"]}

# display COCO categories and supercategories
cats = coco.loadCats(coco.getCatIds())
nms = [cat["name"] for cat in cats]
id_to_name = {cat["id"]: cat["name"] for cat in cats}
print(nms)
print()
# print('COCO categories: \n{}\n'.format(' '.join(nms)))

nms = set([cat["supercategory"] for cat in cats])
# print('COCO supercategories: \n{}'.format(' '.join(nms)))

# get all images containing given categories, select one at random
catIds = coco.getCatIds(catNms=["person"])
imgIds = coco.getImgIds(catIds=catIds)
# imgIds = coco.getImgIds(imgIds = [324158])
# RANDOM IMAGE
img = coco.loadImgs(imgIds[np.random.randint(0, len(imgIds))])[0]

annIds = coco.getAnnIds(imgIds=img["id"])
anns = coco.loadAnns(annIds)

ann_id = anns[0]["category_id"]
# print(catIds)
# print(cats)


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
        details["Loc"] = (left, top, left + width, top + height)
        details["Center"] = get_center(ann["bbox"])
        details["Type"] = "Object"
        details["Name"] = id_to_name[ann["category_id"]]
        details["ImgIndex"] = img_index
        env[str(i + num_objects)] = details
    sorted_objs = sorted(env.items(), key=lambda x: x[1]["Center"][0])
    for i, (_, details) in enumerate(sorted_objs):
        details["ObjPosInImgLeftToRight"] = i
    return env


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


def find_matching_obj(obj, gt_env):
    for obj_id, gt_obj in gt_env.items():
        if obj["Name"] != gt_obj["Name"]:
            continue
        if get_iou(gt_obj["Loc"], obj["Loc"]) > 0.6:
            return obj_id
    return None


def get_mscoco_environment(
    filename, img_index, num_objects, use_prediction_sets, gt_env
):
    print(filename)
    im = cv2.imread(filename)
    outputs = predictor(im)
    bboxes = outputs["instances"].pred_boxes
    classes = [class_names[i] for i in outputs["instances"].pred_classes]
    obj_list = [
        {
            "Name": name.lower(),
            "Loc": bbox.tolist(),
            "Center": get_center(bbox.tolist()),
            "ImgIndex": img_index,
            "Type": "Object",
        }
        for (name, bbox) in zip(classes, bboxes)
    ]
    sorted_objs = sorted(obj_list, key=lambda x: x["Center"][0])
    env = {}
    for i, details in enumerate(sorted_objs):
        details["ObjPosInImgLeftToRight"] = i
        matching_id = find_matching_obj(details, gt_env)
        if matching_id:
            env[matching_id] = details
        else:
            env[str(i + num_objects)] = details
    return env


def preprocess():
    img_folder = "../mscoco/smallcoco/"
    i = 0
    for filename in os.listdir(img_folder):
        img_dir = img_folder + filename
        img_id = filename_to_id[filename]
        annIds = coco.getAnnIds(imgIds=img_id)
        anns = coco.loadAnns(annIds)
        env = {}
        for ann in anns:
            details = {}
            details["Loc"] = ann["bbox"]
            details["Type"] = "Object"
            details["Name"] = id_to_name[ann["category_id"]]
            env[i] = details
            i += 1
    print(env)


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


def make_dataset():
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
    for filename in new_dataset:
        img_dir = img_folder + filename
        shutil.copyfile(img_dir, "./mscoco_images/" + filename)


if __name__ == "__main__":
    make_dataset()

# Some basic setup:
# Setup detectron2 logger
import random
import cv2
import json
from detectron2.data import MetadataCatalog, DatasetCatalog
import os
from detectron2.utils.visualizer import Visualizer
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2 import model_zoo

# from google.colab.patches import cv2_imshow
import numpy as np
import detectron2
from detectron2.utils.logger import setup_logger
from image_utils import *
import statistics

setup_logger()

# im = cv2.imread("./input.jpg")

# cfg = get_cfg()
# # add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
# cfg.merge_from_file(model_zoo.get_config_file(
#     "COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml"))
# cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
# # Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
# cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(
#     "COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml")
# predictor = DefaultPredictor(cfg)
# outputs = predictor(im)

# print(outputs["instances"].pred_classes)
# print(outputs["instances"].pred_boxes)

# predictions = outputs["instances"].to("cpu")
# classes = predictions.pred_classes.tolist(
# ) if predictions.has("pred_classes") else None
# print(classes)

# metadata = MetadataCatalog.get(cfg.DATASETS.TRAIN[0])
# print(type(metadata))
# print(metadata.get("thing_classes"))


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


def get_faster_rcnn_objects(img_name, predictor):
    im = cv2.imread(img_name)
    outputs = predictor(im)
    bboxes = outputs["instances"].pred_boxes
    classes = [class_names[i] for i in outputs["instances"].pred_classes]
    return [
        {"Name": name.lower(), "bbox": bbox.tolist()}
        for (name, bbox) in zip(classes, bboxes)
    ]


def get_rekognition_objects(img_name, client):
    object_response = client.detect_labels(
        Image={"Bytes": get_source_bytes(img_name)}, MaxLabels=100, MinConfidence=75
    )
    img = img = cv2.imread(img_name, 1)
    objects = object_response["Labels"]
    details_maps = []
    for obj in objects:
        for instance in obj["Instances"]:
            if instance["Confidence"] < 75:
                continue
            # Remove redundant objects
            if obj["Name"] in {
                "Adult",
                "Child",
                "Man",
                "Male",
                "Woman",
                "Female",
                "Bride",
                "Groom",
                "Boy",
                "Girl",
                "Teen",
            }:
                continue
            details_map = {}
            details_map["Name"] = obj["Name"].lower()
            details_map["bbox"] = get_loc(img, instance["BoundingBox"])
            details_maps.append(details_map)
    return details_maps


def get_object_lists(predictor):
    env = {}
    i = 0
    for dataset in ["cars", "cats", "guitars", "receipts2", "wedding"]:
        img_folder = "../test_images/" + dataset + "/"
        client.delete_collection(CollectionId="library2")
        client.create_collection(CollectionId="library2")
        for img_name in os.listdir(img_folder):
            img_name = img_folder + img_name
            print(img_name)
            frcnn_objects = get_faster_rcnn_objects(img_name, predictor)
            rek_objects = get_rekognition_objects(img_name, client)
            env[img_name] = {"faster_rcnn": frcnn_objects, "rekognition": rek_objects}
    return env


def find_matching_obj(rek_obj, frcnn_objects):
    for obj in frcnn_objects:
        if obj["Name"] != rek_obj["Name"]:
            continue
        # print("hi")
        # print(get_iou(rek_obj["bbox"], obj["bbox"]))
        if get_iou(rek_obj["bbox"], obj["bbox"]) > 0.75:
            return True
    return False


def save_bad_images(bad_images, env):
    for i, img_name in enumerate(bad_images):
        img = cv2.imread(img_name, 1)
        img1 = draw_rectangles2(img_name, env[img_name]["faster_rcnn"])
        img2 = draw_rectangles2(img_name, env[img_name]["rekognition"])
        comparison = np.concatenate((img1, img2), axis=1)
        cv2.imwrite("../output/{}.png".format(i), comparison)


def compare(env, class_names):
    num_rek_objects = [len(v["rekognition"]) for v in env.values()]
    num_rek_objects_with_frcnn_class = [
        len([obj for obj in v["rekognition"] if obj["Name"] in class_names])
        for v in env.values()
    ]
    num_matched_objects = []
    unmatched_objs = {}
    bad_images = set()
    for k, v in env.items():
        num_matched_objects.append(0)
        frcnn_objects = v["faster_rcnn"]
        rek_objects = v["rekognition"]
        for rek_obj in rek_objects:
            has_matching_obj = find_matching_obj(rek_obj, frcnn_objects)
            if has_matching_obj:
                num_matched_objects[-1] += 1
            else:
                if rek_obj["Name"] == "person":
                    bad_images.add(k)
                if rek_obj["Name"] not in unmatched_objs:
                    unmatched_objs[rek_obj["Name"]] = 0
                unmatched_objs[rek_obj["Name"]] += 1
    pct_matched_objects = [
        a / b for (a, b) in zip(num_matched_objects, num_rek_objects) if b != 0
    ]
    pct_matched_objects_with_frcnn_class = [
        a / b
        for (a, b) in zip(num_matched_objects, num_rek_objects_with_frcnn_class)
        if b != 0
    ]
    avg_percent = statistics.mean(pct_matched_objects_with_frcnn_class)
    unmatched_objs_with_frcnn_class = {
        k: v for (k, v) in unmatched_objs.items() if k in class_names
    }
    print("Faster R-CNN Classes: {}".format(class_names))
    # print("Percent of matched objects per image: {}".format(pct_matched_objects))
    # print("Percent of matched objects per image, only considering objects with Faster R-CNN class: {}".format(
    # pct_matched_objects_with_frcnn_class))
    print(
        "Average percent of matched objects, only considering objects with Faster R-CNN class: {}".format(
            avg_percent
        )
    )

    sorted_unmatched_objs = sorted(
        unmatched_objs.items(), key=lambda x: x[1], reverse=True
    )
    sorted_unmatched_objs_with_frcnn_class = sorted(
        unmatched_objs_with_frcnn_class.items(), key=lambda x: x[1], reverse=True
    )

    print("Unmatched objects: {}".format(sorted_unmatched_objs))
    print(
        "Unmatched objects that have faster R-CNN class: {}".format(
            sorted_unmatched_objs_with_frcnn_class
        )
    )
    save_bad_images(bad_images, env)


if __name__ == "__main__":
    client = get_client()
    predictor, class_names = get_predictor()
    env = get_object_lists(predictor)
    compare(env, class_names)

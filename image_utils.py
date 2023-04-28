import boto3
import copy
import csv
import cv2
import re
from typing import Any, List, Dict
from dsl import Blur, Blackout, Crop, Brighten, Recolor
import numpy as np
import random


# Since we don't construct class here, some static variables to track things
face_hash_to_id: Dict[str, int] = {}
face_id_to_hash: Dict[int, str] = {}


def add_face_hash_id_mapping(hash_code: str, face_id: int):
    global face_id_to_hash
    global face_hash_to_id

    face_id_to_hash[face_id] = hash_code
    face_hash_to_id[hash_code] = face_id


def is_contained(bbox1, bbox2, include_edges=False):
    left1, top1, right1, bottom1 = bbox1
    left2, top2, right2, bottom2 = bbox2
    if include_edges:
        return left1 >= left2 and top1 >= top2 and bottom1 <= bottom2 and right1 <= right2
    else:
        return left1 > left2 and top1 > top2 and bottom1 < bottom2 and right1 < right2


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


def is_unique_text_object(bbox_to_text, new_bbox, new_text):
    for bbox, text in bbox_to_text.items():
        if text == new_text:
            if get_iou(bbox, new_bbox) > 0.5:
                return False
    return True


def get_loc(img, bounding_box):
    img_height, img_width = img.shape[0], img.shape[1]
    left = int(bounding_box["Left"] * img_width)
    top = int(bounding_box["Top"] * img_height)
    right = int(left + (bounding_box["Width"] * img_width))
    bottom = int(top + (bounding_box["Height"] * img_height))
    return (left, top, right, bottom)


def check_regex(text, key):
    regexes = {
        "phone": "^(\\+\\d{1,2}\\s)?\\(?\\d{3}\\)?[\\s.-]?\\d{3}[\\s.-]?\\d{4}$",
        "price": "^\\$?\\d+[.,]\\d{1,2}$",
    }
    return bool(re.match(regexes[key], text))


def get_source_bytes(img: str):
    with open(img, "rb") as source_image:
        source_bytes = source_image.read()
    return source_bytes


def get_client():
    with open("../credentials.csv", "r") as _input:
        next(_input)
        reader = csv.reader(_input)
        for line in reader:
            access_key_id = line[2]
            secret_access_key = line[3]

    client = boto3.client(
        "rekognition", aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key, region_name="us-west-2"
    )
    return client


def get_environment(
    img_dir: str, client, img_index, use_prediction_sets, add_noise, keys=[], prev_environment=None, max_faces=10
) -> Dict[str, Dict[str, Any]]:
    # The same face in a different photo has a different entry in the library,
    # but the SAME Index
    face_responses = []
    text_responses = []
    object_responses = []
    imgs = []
    print("img_dir:", img_dir)
    face_response = client.index_faces(
        CollectionId="library2",
        Image={"Bytes": get_source_bytes(img_dir)},
        MaxFaces=max_faces,
        DetectionAttributes=["ALL"],
    )
    text_response = client.detect_text(
        Image={"Bytes": get_source_bytes(img_dir)})
    object_response = client.detect_labels(
        Image={"Bytes": get_source_bytes(img_dir)}, MaxLabels=100, MinConfidence=75
    )
    img = cv2.imread(img_dir, 1)
    face_responses.append(face_response)
    text_responses.append(text_response)
    object_responses.append(object_response)
    imgs.append(img)
    return get_details(
        face_responses, text_responses, object_responses, keys, imgs, client, img_index, use_prediction_sets, add_noise, prev_environment
    )


def apply_action_to_object(action, img, details_map):
    left, top, right, bottom = details_map["Loc"]
    img_height, img_width = img.shape[0], img.shape[1]
    if isinstance(action, Blur):
        ROI = img[top:bottom, left:right]
        blurred_obj = cv2.GaussianBlur(ROI, (action.value, action.value), 0)
        # Insert ROI back into image
        img[top:bottom, left:right] = blurred_obj
    elif isinstance(action, Brighten):
        ROI = img[top:bottom, left:right]
        hsv = cv2.cvtColor(ROI, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        lim = 255 - action.value
        v[v > lim] = 255
        v[v <= lim] += action.value
        final_hsv = cv2.merge((h, s, v))
        brightened = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        # Insert ROI back into image
        img[top:bottom, left:right] = brightened
    elif isinstance(action, Recolor):
        ROI = img[top:bottom, left:right]
        hsv = cv2.cvtColor(ROI, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        lim = 255 - action.value
        h[h > lim] = 255
        h[h <= lim] += action.value
        final_hsv = cv2.merge((h, s, v))
        brightened = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        # Insert ROI back into image
        img[top:bottom, left:right] = brightened
    elif isinstance(action, Blackout):
        ROI = np.array([[left, top], [right, top], [
                       right, bottom], [left, bottom]])
        cv2.fillPoly(img, pts=[ROI], color=(0, 0, 0))
    return img


def make_sidebar(img):
    img_height, img_width = img.shape[0], img.shape[1]
    sidebar = np.zeros((img_height, 150, 3), np.uint8)
    sidebar.fill(255)
    left = 1
    right = 150 - 1
    top = 1
    box_length = int(img_height/5) - 1
    color = (0, 0, 0)
    thickness = 2
    actions = ["Blur", "Blackout", "Crop", "Undo", "Done"]
    action_to_bb = {}
    for i in range(5):
        top = (box_length * i) + 1
        bottom = (box_length * (i + 1)) - 1
        cv2.rectangle(sidebar, (left, top), (right, bottom), color, thickness)
        action_to_bb[actions[i]] = (
            left + img_width, top, right + img_width, bottom)
        text_horiz = int(img_width/2)
        # text_vert = int((bottom - box_length)/2)
        text_vert = 100
        cv2.putText(sidebar, actions[i], (10, bottom - int(box_length/2)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, thickness)
    return (sidebar, action_to_bb)


def annotate_image(img_dir, env):
    print(img_dir)
    global cur_img_with_rectangles
    global inds
    global action_num
    inds = set()
    img = cv2.imread(img_dir, 1)
    imgs = [(img, env)]
    action_to_objects = []
    sidebar, action_to_bb = make_sidebar(img)
    num_rounds = 0
    while True:
        cur_img, cur_env = imgs[-1]
        cur_img_with_rectangles = draw_rectangles(cur_img.copy(), cur_env)
        # if num_rounds == 0:
        cur_img_with_rectangles = np.concatenate(
            (cur_img_with_rectangles, sidebar), axis=1)
        # Display image
        while True:
            cv2.imshow("image", cur_img_with_rectangles)
            cv2.namedWindow('image')
            cv2.setMouseCallback('image', on_click, (cur_env, action_to_bb))
            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                break
        cv2.destroyAllWindows()
        if int(action_num) == 1:
            action = Blur()
        elif int(action_num) == 2:
            action = Blackout()
        elif int(action_num) == 3:
            action = Crop()
        elif int(action_num) == 4:
            imgs.pop()
            action_to_objects.pop()
            if num_rounds > 0:
                num_rounds -= 1
            inds = set()
            sidebar, action_to_bb = make_sidebar(imgs[-1][0])
            continue
        elif int(action_num) == 5:
            break
        num_rounds += 1
        new_img = cur_img.copy()
        if isinstance(action, Crop):
            new_img, new_env = apply_crop(new_img, cur_env, inds)
            sidebar, action_to_bb = make_sidebar(new_img)
            num_rounds = 0
        else:
            for key, details_map in env.items():
                if details_map["ObjPosInImgLeftToRight"] not in inds:
                    continue
                new_img = apply_action_to_object(action, new_img, details_map)
                new_env = copy.deepcopy(env)
        imgs.append((new_img, new_env))
        action_to_objects.append((action, list(inds)))
        inds = set()
    action_to_objects_dict = {}
    for (action, objects) in action_to_objects:
        if action in action_to_objects_dict:
            action_to_objects_dict[action] += objects
        else:
            action_to_objects_dict[action] = objects
    return action_to_objects_dict


def apply_crop(img, details_map, inds):
    cur_coords = None
    for obj_id, details in details_map.items():
        if details["ObjPosInImgLeftToRight"] not in inds:
            continue
        if cur_coords is None:
            cur_coords = details["Loc"]
        else:
            cur_coords = (
                min(cur_coords[0], details["Loc"][0]),
                min(cur_coords[1], details["Loc"][1]),
                max(cur_coords[2], details["Loc"][2]),
                max(cur_coords[3], details["Loc"][3]),
            )
    left, top, right, bottom = cur_coords
    img = img[top:bottom, left:right]
    new_details_map = {}
    for obj_id, details in details_map.items():
        obj_left, obj_top, obj_right, obj_bottom = details["Loc"]
        if is_contained(details["Loc"], cur_coords, include_edges=True):
            new_details_map[obj_id] = copy.deepcopy(details)
            new_details_map[obj_id]["Loc"] = (
                obj_left - left, obj_top - top, obj_right - left, obj_bottom - top)
    return img, new_details_map


inds = set()
action_num = None


def on_click(event, x, y, flags, params):
    (env, action_to_bb) = params
    green_color = (0, 0, 100)
    red_color = (0, 100, 0)
    black_color = (0, 0, 0)
    thickness = 2
    if event == cv2.EVENT_LBUTTONDOWN:
        global inds
        global action_num
        cur_loc = None
        cur_ind = None
        cur_name = None
        for key, details_map in env.items():
            left, top, right, bottom = details_map["Loc"]
            ind = details_map["ObjPosInImgLeftToRight"]
            name = details_map["Name"] if "Name" in details_map else details_map["Type"]
            if x > left and x < right and y > top and y < bottom:
                if cur_loc is None or get_size(cur_loc) > get_size((left, top, right, bottom)):
                    cur_loc = (left, top, right, bottom)
                    cur_ind = ind
                    cur_name = name
        for i, (action, loc) in enumerate(list(action_to_bb.items())):
            left, top, right, bottom = loc
            if x > left and x < right and y > top and y < bottom:
                cv2.rectangle(cur_img_with_rectangles, (left, top),
                              (right, bottom), red_color, 2)
                action_num = i + 1
                for other_action, other_loc in action_to_bb.items():
                    if action == other_action:
                        continue
                    left, top, right, bottom = other_loc
                    cv2.rectangle(cur_img_with_rectangles,
                                  (left, top), (right, bottom), black_color, 2)
                return
        if cur_loc is None:
            return
        left, top, right, bottom = cur_loc
        if cur_ind not in inds:
            inds.add(cur_ind)
            print("Added " + cur_name)
            cv2.rectangle(cur_img_with_rectangles, (left, top),
                          (right, bottom), green_color, thickness)
        else:
            inds.remove(cur_ind)
            print("Removed " + cur_name)
            cv2.rectangle(cur_img_with_rectangles, (left, top),
                          (right, bottom), red_color, thickness)


def get_size(loc):
    left, top, right, bottom = loc
    return abs(left - right) * abs(top - bottom)


def draw_rectangles(img, env):
    for key, details_map in env.items():
        left, top, right, bottom = details_map["Loc"]
        img_height, img_width = img.shape[0], img.shape[1]
        if right > img_width or bottom > img_height:
            continue
        color = (0, 100, 0)
        thickness = 2
        keys = []
        img = cv2.rectangle(
            img, (left, top), (right, bottom), color, thickness)
    return img


def get_details(
    face_responses,
    text_responses,
    object_responses,
    keys: List[str],
    imgs,
    client,
    img_index,
    use_prediction_sets,
    add_noise,
    prev_environment=None,
    max_faces=10,
) -> Dict[str, Dict[str, Any]]:

    details_list = []

    if not prev_environment:
        obj_count = 0
        img_count = 0
    else:
        obj_count = len(prev_environment)
        img_count = max(item["ImgIndex"]
                        for item in prev_environment.values()) + 1
    for img_index, (face_response, text_response, img) in enumerate(zip(face_responses, text_responses, imgs)):
        faces = face_response["FaceRecords"]
        text_objects = text_response["TextDetections"]
        objects = object_responses[0]["Labels"]
        for face in faces:
            details = face["FaceDetail"]
            face_hash = face["Face"]["FaceId"]
            details_map = {}
            details_map["Type"] = "Face"
            for key in keys:
                if use_prediction_sets:
                    if key in {
                        "Emotions",
                        "AgeRange",
                    }:
                        details_map[key] = details[key]
                    if key in {
                        "Smile",
                        "Eyeglasses",
                        "EyesOpen",
                        "MouthOpen",
                    }:
                        if add_noise and random.random() > .9:
                            details[key]["Confidence"] = random.random() * 100
                        if details[key]["Confidence"] > 75:
                            details_map[key] = [details[key]["Value"]]
                        # These are binary values so we can do this without a problem
                        else:
                            details_map[key] = [True, False]
                else:
                    if key in {"Smile", "Eyeglasses", "EyesOpen", "MouthOpen"}:
                        if add_noise and random.random() > .9:
                            details[key]["Confidence"] = random.random() * 100
                        if details[key]["Confidence"] > 75:
                            # The value doesn't matter here
                            details_map[key] = True
                    if key == "Emotions":
                        details_map[key] = []
                        emotion_list = details[key]
                        for emotion in emotion_list:
                            if emotion["Confidence"] > 75:
                                details_map[key].append(emotion["Type"])
                    elif key == "AgeRange":
                        details_map[key] = details[key]
            details_map["Loc"] = get_loc(img, face["Face"]["BoundingBox"])
            # Check if this face matches another face in the library
            if face_hash in face_hash_to_id:
                face_index = face_hash_to_id[face_hash]
            else:
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
                    matched_face_hashes = [item["Face"]["FaceId"]
                                           for item in search_response["FaceMatches"]]
                    face_index = obj_count
                    for matched_face_hash in matched_face_hashes:
                        if matched_face_hash == face_hash:
                            continue
                        if matched_face_hash in hashes_to_indices:
                            face_index = hashes_to_indices[matched_face_hash]
                            break
            details_map["Index"] = face_index
            details_map["Hash"] = face_hash
            details_map["ImgIndex"] = img_index + img_count
            details_list.append(details_map)
            obj_count += 1
        bbox_to_text = {}
        for text_object in text_objects:
            if text_object["Confidence"] < 75:
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
            for instance in obj["Instances"]:
                if instance["Confidence"] < 75:
                    continue
                # Remove redundant objects
                if obj["Name"] in {'Adult', 'Child', 'Man', 'Male', 'Woman', 'Female', 'Bride', 'Groom', 'Boy', 'Girl'}:
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

    return details_maps

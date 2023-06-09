import csv
from sklearn.metrics import f1_score
import os

tasks = {
    0: {
        "description": "Find all images that contain a car with a person inside (where the person’s face is visible).",
        "dataset": "objects",
        "gt": "car_with_person",
    },
    1: {
        "description": "Find all images with a guitar or a microphone",
        "dataset": "concert2",
        "gt": "guitar_or_microphone",
    },
    2: {
        "description": "Find all images that contain a face that is not smiling.",
        "dataset": "concert2",
        "gt": "not_smiling_face",
    },
    3: {
        "description": "Find all images where Gabe’s face is to the right of Laura’s face.",
        "dataset": "wedding2",
        "gt": "gabe_right_of_laura",
    },
    4: {
        "description": "Find all images with Rachel",
        "dataset": "wedding2",
        "gt": "rachel",
    },
    5: {
        "description": "Find all images that contain a face that is smiling, and has their eyes open.",
        "dataset": "wedding2",
        "gt": "smiling_and_eyes_open",
    },
    6: {
        "description": "Find all images that contain a person whose face you can see.",
        "dataset": "concert2",
        "gt": "person_with_visible_face",
    },
}


def get_study_results():
    for task_id in range(1, 5):
        filename = "output_{}.csv".format(task_id)
        all_files = os.listdir(
            "image-eye-web/public/images/{}".format(tasks[task_id]["dataset"])
        )
        with open(filename) as f:
            reader = csv.reader(f)
            lines = []
            for row in reader:
                lines.append(row)
        if len(lines) < 2:
            continue
        results = {tup[0]: tup[1] for tup in zip(lines[0], lines[1])}
        submitted_images = results["Submitted Images"]
        gt_name = tasks[task_id]["gt"]
        gt = os.listdir("image-eye-web/public/images/ground_truths/{}".format(gt_name))
        gt_labels = [filename in gt for filename in all_files]
        pred_labels = [filename in submitted_images for filename in all_files]
        f1 = f1_score(gt_labels, pred_labels)
        print("Task id: {}".format(task_id))
        print("F1 score: {}".format(f1))
        print()


if __name__ == "__main__":
    get_study_results()

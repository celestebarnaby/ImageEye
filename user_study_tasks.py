import csv
from sklearn.metrics import f1_score
import os

tasks = {
    0: {
        "description": "Find all images that contain a car with a person inside.",
        "dataset": "objects",
        "gt": "car_with_person",
    },
    1: {
        "description": "Find all images with a guitar and a microphone",
        "dataset": "concert2",
        "gt": "guitar_and_microphone",
    },
    2: {
        "description": "Find all images where someone is playing guitar and no one is smiling.",
        "dataset": "concert2",
        "gt": "guitar_and_no_smiles",
    },
    3: {
        "description": "Find all images with no people.",
        "dataset": "concert2",
        "gt": "no_people",
    },
    4: {
        "description": "Find all images with the bride and groom",
        "dataset": "wedding3",
        "gt": "bride_and_groom",
    },
    5: {
        "description": "Find all images where the bride is left of the groom.",
        "dataset": "wedding3",
        "gt": "bride_left_of_groom",
    },
    6: {
        "description": "Find all images that contain the bride and not the groom.",
        "dataset": "wedding3",
        "gt": "bride_and_no_groom",
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

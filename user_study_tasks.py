import sys
import csv
from sklearn.metrics import f1_score
import os
import ast

csv.field_size_limit(sys.maxsize)

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
    # 2: {
    #     "description": "Find all images where someone is playing guitar and no one is smiling.",
    #     "dataset": "concert2",
    #     "gt": "guitar_and_no_smiles",
    # },
    2: {
        "description": "Find all images with no people.",
        "dataset": "concert2",
        "gt": "no_people",
    },
    3: {
        "description": "Find all images with the bride and groom",
        "dataset": "wedding3",
        "gt": "bride_and_groom",
    },
    4: {
        "description": "Find all images where the bride is left of the groom.",
        "dataset": "wedding3",
        "gt": "bride_left_of_groom",
    },
    5: {
        "description": "Find all images that contain the bride and not the groom.",
        "dataset": "wedding3",
        "gt": "bride_and_no_groom",
    },
}


def get_study_results():
    rows = [
        (
            "Task ID",
            "Participant",
            "Task",
            "Tool",
            "Dataset",
            "# Text Queries",
            "# Example Images",
            "Synthesized Programs",
            "F1 Score",
            "F1 Score per Query",
            "# Manually Added Images",
            "# Manually Removed Images",
            "Total Time",
        ),
    ]
    for participant in {"5", "6"}:
        folder = "./{}/".format(participant)
        for results_filename in os.listdir(folder):
            if results_filename == ".DS_Store":
                continue
            print(results_filename)
            task_id = int(results_filename[-5])
            if task_id == 0:
                continue
            img_dir = "image-eye-web/public/images/{}/".format(
                tasks[task_id]["dataset"]
            )
            all_files = os.listdir(img_dir)
            all_files = [img_dir + file for file in all_files]
            with open(folder + results_filename) as f:
                reader = csv.reader(f)
                lines = []
                for row in reader:
                    lines.append(row)
            if len(lines) < 2:
                continue
            results = {tup[0]: tup[1] for tup in zip(lines[0], lines[1])}
            submitted_images = ast.literal_eval(results["Submitted Images"])
            gt_name = tasks[task_id]["gt"]
            gt = os.listdir(
                "image-eye-web/public/images/ground_truths/{}".format(gt_name)
            )
            gt = [img_dir + file for file in gt]
            gt_labels = [filename in gt for filename in all_files]
            pred_labels = [filename in submitted_images for filename in all_files]
            f1 = f1_score(gt_labels, pred_labels)
            print("Task id: {}".format(task_id))
            print("F1 score: {}".format(f1))
            print()
            f1_per_query = []
            if results_filename.startswith("baseline"):
                for result_files in ast.literal_eval(
                    results["Text Query Results"]
                ) + ast.literal_eval(results["Image Query Results"]):
                    pred_labels = [filename in result_files for filename in all_files]
                    f1_per_query.append(f1_score(gt_labels, pred_labels))
                rows.append(
                    (
                        task_id,
                        participant,
                        results["Task"],
                        "Baseline",
                        results["Dataset"],
                        len(ast.literal_eval(results["Text Queries"])),
                        "N/A",
                        "N/A",
                        f1,
                        f1_per_query,
                        len(ast.literal_eval(results["Manually Added"])),
                        len(ast.literal_eval(results["Manually Removed"])),
                        results["Total Time"],
                    )
                )
            else:
                for result_files in ast.literal_eval(results["Synthesis Results"]):
                    pred_labels = [filename in result_files for filename in all_files]
                    f1_per_query.append(f1_score(gt_labels, pred_labels))
                rows.append(
                    (
                        task_id,
                        participant,
                        results["Task"],
                        "ImageEye",
                        results["Dataset"],
                        len(ast.literal_eval(results["Text Queries"])),
                        len(ast.literal_eval(results["Example Images"])),
                        results["Synthesized Programs"],
                        f1,
                        f1_per_query,
                        len(ast.literal_eval(results["Manually Added Images"])),
                        len(ast.literal_eval(results["Manually Removed Images"])),
                        results["Total Time"],
                    )
                )
    with open("results.csv", "w") as f:
        fw = csv.writer(f)
        for row in rows:
            fw.writerow(row)


if __name__ == "__main__":
    get_study_results()

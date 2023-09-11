import sys
import csv
from sklearn.metrics import f1_score
import os
import ast
import itertools
from statistics import mean, median
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import json

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


def get_f1_score(imgs, task_id):
    img_dir = "image-eye-web/public/images/{}/".format(tasks[task_id]["dataset"])
    all_files = os.listdir(img_dir)
    all_files = [img_dir + file for file in all_files]
    gt_name = tasks[task_id]["gt"]
    gt = os.listdir("image-eye-web/public/images/ground_truths/{}".format(gt_name))
    gt = [img_dir + file for file in gt]
    gt_labels = [filename in gt for filename in all_files]
    pred_labels = [filename in imgs for filename in all_files]
    return f1_score(gt_labels, pred_labels)


def get_gt_sizes():
    for task in [1, 2, 4, 5]:
        img_dir = "image-eye-web/public/images/{}/".format(tasks[task]["dataset"])
        all_files = os.listdir(img_dir)
        all_files = [img_dir + file for file in all_files]
        gt_name = tasks[task]["gt"]
        gt = os.listdir("image-eye-web/public/images/ground_truths/{}".format(gt_name))
        gt = [img_dir + file for file in gt]
        # gt_labels = [filename in gt for filename in all_files]
        print(task)
        print(len(gt))
        print()


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
            "Synthesized Program per Query",
            "F1 Score of Submitted Images",
            "F1 Score per Query",
            "F1 Score of Saved Images Over Time",
            "# Manually Added Images",
            "# Manually Removed Images",
            "Total Time",
        ),
    ]
    for participant in {
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
        "29",
        "30",
        "31",
        "32",
    }:
        folder = "./user_study_results/{}/".format(participant)
        for results_filename in os.listdir(folder):
            if results_filename == ".DS_Store":
                continue
            print(results_filename)
            task_id = int(results_filename[-5])
            if task_id == 0:
                continue
            # img_dir = "image-eye-web/public/images/{}/".format(
            # tasks[task_id]["dataset"]
            # )
            # all_files = os.listdir(img_dir)
            # all_files = [img_dir + file for file in all_files]
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
            # gt = [img_dir + file for file in gt]
            # gt_labels = [filename in gt for filename in all_files]
            # pred_labels = [filename in submitted_images for filename in all_files]
            # f1 = f1_score(gt_labels, pred_labels)
            f1 = get_f1_score(submitted_images, task_id)
            print("Task id: {}".format(task_id))
            print("F1 score: {}".format(f1))
            print()
            f1_per_query = []
            if results_filename.startswith("baseline"):
                for result_files, time in ast.literal_eval(
                    results["Text Query Results"]
                ) + ast.literal_eval(results["Image Query Results"]):
                    # pred_labels = [filename in result_files for filename in all_files]
                    # f1_per_query.append(f1_score(gt_labels, pred_labels))
                    f1_per_query.append((get_f1_score(result_files, task_id), time))
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
                        ast.literal_eval(results["Saved Images F1 Over Time"]),
                        len(ast.literal_eval(results["Manually Added"])),
                        len(ast.literal_eval(results["Manually Removed"])),
                        results["Total Time"],
                    )
                )
            else:
                for result_files, time in ast.literal_eval(
                    results["Search Results per Query"]
                ):
                    # pred_labels = [filename in result_files for filename in all_files]
                    # f1_per_query.append((f1_score(gt_labels, pred_labels), time))
                    f1_per_query.append((get_f1_score(result_files, task_id), time))
                rows.append(
                    (
                        task_id,
                        participant,
                        results["Task"],
                        "ImageEye",
                        results["Dataset"],
                        len(ast.literal_eval(results["Text Queries"])),
                        mean(
                            [
                                len(x)
                                for x in (ast.literal_eval(results["Example Images"]))
                            ]
                        ),
                        results["Synthesized Program per Query"],
                        f1,
                        f1_per_query,
                        ast.literal_eval(results["Saved Images F1 Over Time"]),
                        len(ast.literal_eval(results["Manually Added Images"])),
                        len(ast.literal_eval(results["Manually Removed Images"])),
                        results["Total Time"],
                    )
                )
    with open("results_per_study.csv", "w") as f:
        fw = csv.writer(f)
        for row in rows:
            fw.writerow(row)
    # results_per_task_and_tool = {}
    overall_rows = [
        [
            "Task",
            "Tool",
            "N",
            "Average F1 Score of Submitted Results",
            "Average F1 Score of Best Query",
            "Average F1 Score of Saved Images after 30 seconds",
            "Average F1 Score of Saved Images after 60 seconds",
            "Average F1 Score of Saved Images after 120 seconds",
            "Average # manually edited/removed images",
            "Average # of example images",
            "Average # of Text Queries",
            "Median F1 Score of Submitted Results",
            "Median F1 Score of Best Query",
            "Median F1 Score of Saved Images after 30 seconds",
            "Median F1 Score of Saved Images after 60 seconds",
            "Median F1 Score of Saved Images after 120 seconds",
            "Median # manually edited/removed images",
            "Median # of example images",
            "Median # of Text Queries",
        ]
    ]
    task_names = [1, 2, 4, 5, "overall"]
    tools = ["Baseline", "ImageEye"]
    rows = rows[1:]
    for task, tool in itertools.product(*[task_names, tools]):
        if task == "overall":
            overall_rows.append(
                [
                    task,
                    tool,
                    len([row for row in rows if row[3] == tool]),
                    mean([row[8] for row in rows if row[3] == tool]),
                    mean([max(row[9])[0] for row in rows if row[3] == tool]),
                    mean(
                        [
                            get_score_within_n_seconds(row[10], 30)
                            for row in rows
                            if row[3] == tool
                            and get_score_within_n_seconds(row[10], 30) >= 0
                        ]
                    ),
                    mean(
                        [
                            get_score_within_n_seconds(row[10], 60)
                            for row in rows
                            if row[3] == tool
                            and get_score_within_n_seconds(row[10], 60) >= 0
                        ]
                    ),
                    mean(
                        [
                            get_score_within_n_seconds(row[10], 120)
                            for row in rows
                            if row[3] == tool
                            and get_score_within_n_seconds(row[10], 120) >= 0
                        ]
                    ),
                    mean([row[11] + row[12] for row in rows if row[3] == tool]),
                    mean([row[6] for row in rows if row[3] == tool])
                    if tool == "ImageEye"
                    else "N/A",
                    mean([row[5] for row in rows if row[3] == tool]),
                    median([row[8] for row in rows if row[3] == tool]),
                    median([max(row[9])[0] for row in rows if row[3] == tool]),
                    median(
                        [
                            get_score_within_n_seconds(row[10], 30)
                            for row in rows
                            if row[3] == tool
                        ]
                    ),
                    median(
                        [
                            get_score_within_n_seconds(row[10], 60)
                            for row in rows
                            if row[3] == tool
                        ]
                    ),
                    median(
                        [
                            get_score_within_n_seconds(row[10], 120)
                            for row in rows
                            if row[3] == tool
                        ]
                    ),
                    median([row[11] + row[12] for row in rows if row[3] == tool]),
                    median([row[6] for row in rows if row[3] == tool])
                    if tool == "ImageEye"
                    else "N/A",
                    median([row[5] for row in rows if row[3] == tool]),
                ]
            )
            continue
        overall_rows.append(
            [
                task,
                tool,
                len([row for row in rows if row[0] == task and row[3] == tool]),
                mean([row[8] for row in rows if row[0] == task and row[3] == tool]),
                mean(
                    [
                        max(row[9])[0]
                        for row in rows
                        if row[0] == task and row[3] == tool
                    ]
                ),
                mean(
                    [
                        get_score_within_n_seconds(row[10], 30)
                        for row in rows
                        if row[0] == task and row[3] == tool
                    ]
                ),
                mean(
                    [
                        get_score_within_n_seconds(row[10], 60)
                        for row in rows
                        if row[0] == task and row[3] == tool
                    ]
                ),
                mean(
                    [
                        get_score_within_n_seconds(row[10], 120)
                        for row in rows
                        if row[0] == task and row[3] == tool
                    ]
                ),
                mean(
                    [
                        row[11] + row[12]
                        for row in rows
                        if row[0] == task and row[3] == tool
                    ]
                ),
                mean([row[6] for row in rows if row[0] == task and row[3] == tool])
                if tool == "ImageEye"
                else "N/A",
                mean([row[5] for row in rows if row[0] == task and row[3] == tool]),
                median([row[8] for row in rows if row[0] == task and row[3] == tool]),
                median(
                    [
                        max(row[9])[0]
                        for row in rows
                        if row[0] == task and row[3] == tool
                    ]
                ),
                median(
                    [
                        get_score_within_n_seconds(row[10], 30)
                        for row in rows
                        if row[0] == task and row[3] == tool
                    ]
                ),
                median(
                    [
                        get_score_within_n_seconds(row[10], 60)
                        for row in rows
                        if row[0] == task and row[3] == tool
                    ]
                ),
                median(
                    [
                        get_score_within_n_seconds(row[10], 120)
                        for row in rows
                        if row[0] == task and row[3] == tool
                    ]
                ),
                median(
                    [
                        row[11] + row[12]
                        for row in rows
                        if row[0] == task and row[3] == tool
                    ]
                ),
                median([row[6] for row in rows if row[0] == task and row[3] == tool])
                if tool == "ImageEye"
                else "N/A",
                median([row[5] for row in rows if row[0] == task and row[3] == tool]),
            ]
        )
    with open("overall_results.csv", "w") as f:
        fw = csv.writer(f)
        for row in overall_rows:
            fw.writerow(row)

    # make_line_plot(rows)
    do_ttest(rows)


def do_ttest(rows):
    for task in [1, 2, 4, 5, "overall"]:
        if task == "overall":
            imageeye_scores = [
                row[11] + row[12] + row[6] for row in rows if row[3] == "ImageEye"
            ]
            baseline_scores = [
                row[11] + row[12] for row in rows if row[3] == "Baseline"
            ]
        else:
            imageeye_scores = [
                row[11] + row[12] + row[6]
                for row in rows
                if row[0] == task and row[3] == "ImageEye"
            ]
            baseline_scores = [
                row[11] + row[12]
                for row in rows
                if row[0] == task and row[3] == "Baseline"
            ]
        imageeye_group = np.array(imageeye_scores)
        baseline_group = np.array(baseline_scores)
        print()
        print(task)
        print("Variance: {}, {}".format(np.var(imageeye_group), np.var(baseline_group)))
        print(stats.ranksums(imageeye_group, baseline_group))
        print()


def make_line_plot(rows):
    plt.rcParams["font.family"] = "Times New Roman"
    imageeye_times = []
    baseline_times = []
    for i in range(0, 330, 30):
        if i == 0:
            imageeye_times.append((0, 0))
            baseline_times.append((0, 0))
            continue
        imageeye_times.append(
            (
                mean(
                    [
                        get_score_within_n_seconds(row[9], i)
                        for row in rows
                        if row[3] == "ImageEye"
                        and get_score_within_n_seconds(row[9], i) >= 0
                    ]
                ),
                i,
            )
        )
        baseline_times.append(
            (
                mean(
                    [
                        get_score_within_n_seconds(row[9], i)
                        for row in rows
                        if row[3] == "Baseline"
                        and get_score_within_n_seconds(row[9], i) >= 0
                    ]
                ),
                i,
            )
        )
    plt.plot(
        [t[1] for t in imageeye_times],
        [t[0] for t in imageeye_times],
        label="PhotoScout",
        color="blue",
        linestyle="-",
        marker="o",
    )
    plt.plot(
        [t[1] for t in baseline_times],
        [t[0] for t in baseline_times],
        label="CLIPWrapper",
        color="orange",
        linestyle="--",
        marker="s",
    )
    plt.xlabel("Time (s)")
    plt.ylabel("Average F1 Score of Best Query")

    plt.xticks(range(0, 330, 30))

    plt.legend()
    plt.savefig("f1_over_time.jpeg", dpi=300)


def get_score_within_n_seconds(l, n):
    scores_within_n_seconds = [x[0] for x in l if x[1] < n]
    if len(scores_within_n_seconds) > 0:
        return max(scores_within_n_seconds)
    else:
        return -1


def analyze_qual_data():
    rows = [
        [
            "Task",
            "Tool",
            "N",
            "Average Ease of Use",
            "Average Confidence in Results",
        ]
    ]
    data = []
    with open("qual.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    data = data[1:]
    for task in [0, 1, 2, 3]:  # "overall"]:
        for tool in ["A", "B"]:
            # if task == "overall":
            #     rows.append(
            #         [
            #             task,
            #             tool,
            #             len(
            #                 [
            #                     float(item[task * 3 + 2])
            #                     for item in data
            #                     if item[task * 3 + 1] != "N/A"
            #                 ]
            #             ),
            #             mean(
            #                 [
            #                     float(item[task * 3 + 1])
            #                     for item in data
            #                     if item[task * 3 + 1] != "N/A"
            #                 ]
            #             ),
            #             mean(
            #                 [
            #                     float(item[task * 3 + 2])
            #                     for item in data
            #                     if item[task * 3 + 1] != "N/A"
            #                 ]
            #             ),
            #         ]
            #     )
            #     continue
            rows.append(
                [
                    task,
                    tool,
                    len(
                        [
                            float(item[task * 3 + 2])
                            for item in data
                            if item[task * 3 + 3] == tool
                            and item[task * 3 + 1] != "N/A"
                        ]
                    ),
                    mean(
                        [
                            float(item[task * 3 + 1])
                            for item in data
                            if item[task * 3 + 3] == tool
                            and item[task * 3 + 1] != "N/A"
                        ]
                    ),
                    mean(
                        [
                            float(item[task * 3 + 2])
                            for item in data
                            if item[task * 3 + 3] == tool
                            and item[task * 3 + 1] != "N/A"
                        ]
                    ),
                ]
            )
    with open("qual_results.csv", "w") as f:
        fw = csv.writer(f)
        for row in rows:
            fw.writerow(row)
    make_bar_plot(data, 1)


def make_bar_plot(data, n):
    plt.rcParams["font.family"] = "Times New Roman"
    tasks = [
        "Guitar and Microphone",
        "No People",
        "Bride Left\n of Groom",
        "Bride and\n Not Groom",
    ]

    imageeye_data = {
        task: [
            float(item[task * 3 + n])
            for item in data
            if item[task * 3 + 3] == "B" and item[task * 3 + n] != "N/A"
        ]
        for task in [0, 1, 2, 3]
    }
    baseline_data = {
        task: [
            float(item[task * 3 + n])
            for item in data
            if item[task * 3 + 3] == "A" and item[task * 3 + n] != "N/A"
        ]
        for task in [0, 1, 2, 3]
    }
    print(imageeye_data)
    print(baseline_data)
    output_data = {"PhotoScout": imageeye_data, "Baseline": baseline_data}
    with open("ease_of_use.json", "w") as outfile:
        json.dump(output_data, outfile)

    X_axis = np.arange(len(tasks))
    imageeye_data = [
        mean(
            [
                float(item[task * 3 + n])
                for item in data
                if item[task * 3 + 3] == "B" and item[task * 3 + n] != "N/A"
            ]
        )
        for task in [0, 1, 2, 3]
    ]
    baseline_data = [
        mean(
            [
                float(item[task * 3 + n])
                for item in data
                if item[task * 3 + 3] == "A" and item[task * 3 + n] != "N/A"
            ]
        )
        for task in [0, 1, 2, 3]
    ]
    plt.bar(
        X_axis - 0.2,
        baseline_data,
        0.4,
        label="CLIPWrapper",
        color="darkorange",
        edgecolor="black",
    )
    plt.bar(
        X_axis + 0.2,
        imageeye_data,
        0.4,
        label="PhotoScout",
        color="cornflowerblue",
        edgecolor="black",
    )
    plt.xticks(X_axis, tasks)
    plt.yticks([0, 1, 2, 3, 4, 5])
    plt.xlabel("Tasks")
    plt.ylabel("Average Score (1-5)")
    plt.title("User-Reported Confidence in Results")
    plt.legend()

    for i, val in enumerate(imageeye_data):
        plt.text(i + 0.1, val + 0.05, str(round(val, 2)))

    for i, val in enumerate(baseline_data):
        plt.text(i - 0.3, val + 0.05, str(round(val, 2)))

    plt.savefig("confidence.jpeg", dpi=300)


def analyze_qs():
    with open("confidence.json") as f:
        data = json.load(f)
    for task in ["0", "1", "2", "3"]:
        tool_res = np.array(data["PhotoScout"][task])
        baseline_res = np.array(data["Baseline"][task])
        print()
        print(task)
        print("Variance: {}, {}".format(np.var(tool_res), np.var(baseline_res)))
        print(stats.ranksums(tool_res, baseline_res))
        print()

    # tool_avg = mean(
    #     sum([data["PhotoScout"][task] for task in ["0", "1", "2", "3"]], [])
    # )
    # baseline_avg = mean(
    #     sum([data["Baseline"][task] for task in ["0", "1", "2", "3"]], [])
    # )
    # print(tool_avg)
    # print(baseline_avg)


if __name__ == "__main__":
    # get_study_results()
    # analyze_qual_data()
    # get_gt_sizes()
    analyze_qs()

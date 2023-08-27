import os
from dsl import *
from synthesizer import *
from interpreter import compare_with_ground_truth
from benchmarks import benchmarks, get_ast_depth, get_ast_size
import cProfile
import time
import io
import pstats
import statistics


def get_dataset_info():
    data = []
    for dataset in ["wedding", "receipts2", "objects"]:
        if dataset == "objects":
            img_to_environment = {}
            for name in ["cars", "cats", "guitars"]:
                img_folder = "../test_images/" + name + "/"
                temp = preprocess(img_folder, args.max_faces)
                img_to_environment = img_to_environment | temp
        else:
            img_folder = "../test_images/" + dataset + "/"
            img_to_environment = preprocess(img_folder, args.max_faces)
        num_objects_per_img = [
            len(env["environment"]) for env in img_to_environment.values()
        ]
        median_objs = statistics.median(num_objects_per_img)
        avg_objs = statistics.mean(num_objects_per_img)
        num_images = len(img_to_environment)
        prog_size_per_benchmark = [
            benchmark.ast_size
            for benchmark in benchmarks
            if (
                benchmark.dataset_name == dataset
                or dataset == "objects"
                and benchmark.dataset_name in ["cars", "cats", "guitars"]
            )
        ]
        prog_depth_per_benchmark = [
            benchmark.ast_depth
            for benchmark in benchmarks
            if (
                benchmark.dataset_name == dataset
                or dataset == "objects"
                and benchmark.dataset_name in ["cars", "cats", "guitars"]
            )
        ]
        avg_prog_size = statistics.mean(prog_size_per_benchmark)
        avg_prog_depth = statistics.mean(prog_depth_per_benchmark)
        num_benchmarks = len(prog_size_per_benchmark)
        row = (
            dataset,
            num_images,
            median_objs,
            avg_objs,
            num_benchmarks,
            avg_prog_size,
            avg_prog_depth,
        )
        data.append(row)

    if not os.path.exists("data"):
        os.mkdir("data")
    name = "data/dataset_info.csv"
    with open(name, "w") as f:
        fw = csv.writer(f)
        fw.writerow(
            (
                "Dataset Name",
                "# Images",
                "Median # Objects Per Image",
                "Average # Objects Per Image",
                "# Synthesis Tasks",
                "Average size of ground truth program",
                "Average depth of ground truth program",
            ),
        )
        for row in data:
            fw.writerow(row)


def test_synthesis(args):
    # if args.get_dataset_info:
    # get_dataset_info()

    if not os.path.exists("data"):
        os.mkdir("data")

    synth = Synthesizer(args, {})

    data = []
    pr = cProfile.Profile()
    pr.enable()
    benchmark_to_example_imgs = {}
    for i, benchmark in enumerate(benchmarks):
        if args.benchmark_set and args.benchmark_set != benchmark.dataset_name:
            continue
        img_folder = "../test_images/" + benchmark.dataset_name + "/"
        img_to_environment, _ = preprocess(img_folder, args.max_faces)
        synth.img_to_environment = img_to_environment
        prog = benchmark.gt_prog
        # signal.signal(signal.SIGALRM, handler)
        # signal.alarm(args.time_limit)
        start_time = time.perf_counter()
        # try:
        example_imgs = (
            [img_folder + img for img in benchmark.example_imgs]
            if args.use_examples
            else []
        )
        (
            synth_prog,
            total_time,
            rounds,
            img_dirs,
            num_objects,
            num_attributes,
        ) = synth.perform_synthesis(
            args,
            gt_prog=prog,
            example_imgs=example_imgs,
            testing=True,
        )
        if args.manually_inspect:
            correct_pct = compare_with_ground_truth(
                synth_prog, img_to_environment, benchmark.desc
            )
        else:
            correct_pct = 0
        benchmark_to_example_imgs[i] = img_dirs
        if args.interactive:
            break
        end_time = time.perf_counter()
        # total_time = end_time - start_time
        correct = (
            synth_prog is not None
            and synth_prog != "TIMEOUT"
            and not synth.get_differing_images(prog, synth_prog)
        )
        row = (
            str(prog),
            str(synth_prog),
            benchmark.dataset_name,
            correct,
            total_time,
            rounds,
            num_objects,
            num_attributes,
            benchmark.desc,
            benchmark.ast_depth,
            benchmark.ast_size,
            correct_pct,
        )
        data.append(row)

    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats()
    with open("data/profiling.txt", "w") as f:
        f.write(s.getvalue())
    ablation_name = ""
    if args.no_equiv_reduction:
        ablation_name += "_NO_EQUIV_REDUCTION"
    if args.no_partial_eval:
        ablation_name += "_NO_PARTIAL_EVAL"
    if args.no_goal_inference:
        ablation_name += "_NO_GOAL_INFERENCE"
    name = "data/synthesis" + ablation_name + ".csv"
    print(name)
    print("writing data to " + name)
    print(os.getcwd())
    with open(name, "w") as f:
        fw = csv.writer(f)
        fw.writerow(
            (
                "Ground Truth Prog",
                "Synthesized Prog",
                "Dataset",
                "Correct",
                "Total Time",
                "# Examples",
                "# Objects",
                "# Attributes",
                "Description",
                "AST Depth",
                "AST Size",
                "% Output Images matching Ground Truth",
            ),
        )
        for row in data:
            fw.writerow(row)
    with open("example_imgs.json", "w") as f:
        json.dump(benchmark_to_example_imgs, f)
    write_logs(synth.logs)
    write_synthesis_overview(synth.synthesis_overview, ablation_name)


clicks = []
num = 10000


# function to display the coordinates of
# of the points clicked on the image
def click_event(event, x, y, flags, params):
    global clicks
    global num
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
        # displaying the coordinates
        # on the Shell
        print(x, " ", y)
        clicks.append((x, y))
        env = params[0]
        if len(clicks) % 2 == 0:
            bbox = [clicks[-2][0], clicks[-2][1], clicks[-1][0], clicks[-1][1]]
            flower_obj = {
                "Type": "Object",
                "Name": "Flowers",
                "Description": "Flowers",
                "Loc": bbox,
            }
            env[str(num)] = flower_obj
            num += 1
            print("obj added!")


def add_flowers():
    img_folder = "image-eye-web/public/images/wedding3/"
    # img_to_environment, obj_strs = preprocess(img_folder, 100)
    key = img_folder + " 2 " + str(100)
    if os.path.exists("./test_images_ui.json"):
        with open("./test_images_ui.json", "r") as fp:
            test_images = json.load(fp)
            if key in test_images:
                img_to_environment = test_images[key]
    for img_name, env in img_to_environment.items():
        env = env["environment"]
        # reading the image
        img = cv2.imread(img_name, 1)

        # displaying the image
        cv2.imshow("image", img)

        # setting mouse handler for the image
        # and calling the click_event() function
        cv2.setMouseCallback("image", click_event, [env])

        # wait for a key to be pressed to exit
        cv2.waitKey(0)

        # close the window
        cv2.destroyAllWindows()
    test_images[key] = img_to_environment
    with open("test_images_ui.json", "w") as fp:
        json.dump(test_images, fp)


if __name__ == "__main__":
    args = get_args()
    add_flowers()
    # test_synthesis(args)

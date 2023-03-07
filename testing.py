import os
from dsl import *
from synthesizer import *
from interpreter import get_client
from benchmarks import benchmarks, get_ast_depth, get_ast_size
import cProfile
import time
import signal
import io
import pstats
import argparse
import itertools
import random
import statistics


def get_dataset_info():
    data = []
    for dataset in ["wedding", "receipts2", "objects"]:
        if dataset == "objects":
            img_to_environment = {}
            for name in ["cars", "cats", "guitars"]:
                img_folder = "test_images/" + name + "/"
                temp = preprocess(img_folder, args.max_faces) 
                img_to_environment = img_to_environment | temp
        else:
            img_folder = "test_images/" + dataset + "/"
            img_to_environment = preprocess(img_folder, args.max_faces)
        num_objects_per_img = [len(env['environment']) for env in img_to_environment.values()]
        median_objs = statistics.median(num_objects_per_img)
        avg_objs = statistics.mean(num_objects_per_img)
        num_images = len(img_to_environment)
        prog_size_per_benchmark = [benchmark.ast_size for benchmark in benchmarks if (benchmark.dataset_name == dataset or dataset == 'objects' and benchmark.dataset_name in ["cars", "cats", "guitars"])]
        prog_depth_per_benchmark = [benchmark.ast_depth for benchmark in benchmarks if (benchmark.dataset_name == dataset or dataset == 'objects' and benchmark.dataset_name in ["cars", "cats", "guitars"])]
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
            avg_prog_depth
        )
        data.append(row)

    if not os.path.exists('data'):
        os.mkdir('data')    
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
                "Average depth of ground truth program"
            ),
        )
        for row in data:
            fw.writerow(row)


def test_synthesis(args):

    # if args.get_dataset_info:
        # get_dataset_info()

    if not os.path.exists("data"):
        os.mkdir("data")

    client = get_client()
    client.delete_collection(CollectionId="library")
    client.create_collection(CollectionId="library")
    synth = Synthesizer(args, client, {})

    data = []
    pr = cProfile.Profile()
    pr.enable()
    benchmark_to_example_imgs = {}
    for i, benchmark in enumerate(benchmarks):
        if args.benchmark_set and args.benchmark_set != benchmark.dataset_name:
            continue
        img_folder = "test_images/" + benchmark.dataset_name + "/"
        img_to_environment = preprocess(img_folder, args.max_faces)
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
        )
        data.append(row)

    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats()
    with open("data/profiling.txt", "w") as f:
        f.write(s.getvalue())
    name = "data/synthesis.csv"
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
            ),
        )
        for row in data:
            fw.writerow(row)
    with open("example_imgs.json", "w") as f:
        json.dump(benchmark_to_example_imgs, f)
    write_logs(synth.logs)
    write_synthesis_overview(synth.synthesis_overview)


if __name__ == "__main__":

    args = get_args()

    test_synthesis(args)

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

def test_synthesis(args):

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
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(args.time_limit)
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
            gt_prog=prog,
            example_imgs=example_imgs,
            interactive=args.interactive,
            testing=True,
            time_limit=args.time_limit,
        )
        benchmark_to_example_imgs[i] = img_dirs
        # except TimeOutException:
        #     """
        #     NOTE: I added a TimeOutException. You never know what exception perform_synthesis_v1 throws
        #     """
        #     row = (str(prog), "TIMEOUT")
        #     data.append(row)
        #     benchmark_to_example_imgs[i] = benchmark.example_imgs
        #     print("TIMEOUT")
        #     continue
        # except:
        # #     """
        # #     TODO: add something else here to handle other exceptions
        # #     """
        #     raise NotImplementedError
        if args.interactive:
            break
        end_time = time.perf_counter()
        # total_time = end_time - start_time
        correct = (
            synth_prog is not None
            and synth_prog != "TIMEOUT"
            and not synth.get_differing_images(prog, synth_prog)
        )
        # num_states = len(fta.states) if fta is not None else 0
        # num_transitions = len(fta.transitions) if fta is not None else 0
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

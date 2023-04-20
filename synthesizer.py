from interpreter import eval_extractor, partial_eval, eval_apply_action
import heapq as hq
import itertools
import signal
from utils import *
from image_utils import *
from tkinter import *
from tkinter import filedialog


def get_prog_output(prog, env, parent):
    if (
        isinstance(prog, Union)
        or isinstance(prog, Intersection)
        or isinstance(prog, Complement)
        or isinstance(prog, Map)
        or isinstance(prog, MatchesWord)
        or isinstance(prog, GetFace)
        or isinstance(prog, IsObject)
        or isinstance(prog, AboveAge)
        or isinstance(prog, BelowAge)
    ):
        return None
    if isinstance(parent, MatchesWord):
        prog = MatchesWord(prog)
    elif isinstance(parent, GetFace):
        prog = GetFace(prog)
    elif isinstance(parent, IsObject):
        prog = IsObject(prog)
    elif isinstance(parent, AboveAge):
        prog = AboveAge(prog)
    elif isinstance(parent, BelowAge):
        prog = BelowAge(prog)
    return eval_extractor(prog, env)


def get_attributes(output_over, output_under, dataset=None):
    return [
        (IsFace(), [], [], [], 0),
        (IsText(), [], [], [], 0),
        (IsPrice(), [], [], [], 0),
        (IsPhoneNumber(), [], [], [], 0),
        (IsSmiling(), [], [], [], 0),
        (EyesOpen(), [], [], [], 0),
        (MouthOpen(), [], [], [], 0),
        (MatchesWord(None), ["word"], [output_over], [output_under], 1),
        (IsObject(None), ["obj"], [output_over], [output_under], 0),
        (GetFace(None), ["index"], [output_over], [output_under], 1),
        (BelowAge(18), [], [], [], 0),
    ]


def get_extractors(
    parent_extr: Extractor, output_over, output_under, env
) -> List[Extractor]:
    extrs = get_attributes(output_over, output_under)
    extrs += (
        (
            Complement(None),
            ["extr"],
            [set(env.keys()) - output_under],
            [set(env.keys()) - output_over],
            1,
        ),
    )
    if not isinstance(parent_extr, Union):
        for i in range(2, 4):
            extrs.append(
                (Union([None] * i), ["extr"] * i,
                 [output_over] * i, [set()] * i, i)
            ),
    if not isinstance(parent_extr, Intersection):
        for i in range(2, 4):
            extrs.append(
                (
                    Intersection([None] * i),
                    ["extr"] * i,
                    [set(env.keys())] * i,
                    [output_under] * i,
                    i,
                )
            ),
    # map_weight = 5 if isinstance(parent_extr, Map) else 3
    map_weight = 3
    extrs += [
        (
            Map(None, None, pos),
            ["extr", "attr"],
            [set(env.keys()), set(env.keys())],
            [set(), output_under],
            map_weight,
        )
        for pos in get_positions()
    ]
    return extrs


# class IOExample:
#     def __init__(
#         self,
#         trace,
#         img_dirs: List[str],
#         client,
#         gt_prog: str,
#         explanation: str,
#         max_faces: int,
#         prev_env=None,
#         img_to_environment=None,
#     ):
#         self.trace = trace
#         self.img_dirs = img_dirs
#         self.gt_prog = gt_prog
#         self.explanation = explanation
#         if img_to_environment:
#             env = {}
#             for img_dir in img_dirs:
#                 env = {**env, **img_to_environment[img_dir]["environment"]}
#             self.env = env
#         else:
#             self.env = get_environment(
#                 img_dirs, client, DETAIL_KEYS, prev_env, max_faces
#             )
#         for details_map in self.env.values():
#             if "ActionApplied" in details_map:
#                 del details_map["ActionApplied"]
#         for action, l in trace.items():
#             for (img_index, index) in l:
#                 for details_map in self.env.values():
#                     if (
#                         details_map["ObjPosInImgLeftToRight"] == index
#                         and details_map["ImgIndex"] == img_index
#                     ):
#                         details_map["ActionApplied"] = action
#         self.obj_list = self.env.keys()


class Tree:
    def __init__(self, _id: int):
        self.id: int = _id
        self.nodes: Dict[int, Extractor] = {}
        self.to_children: Dict[int, List[int]] = {}
        self.to_parent: Dict[int, int] = {}
        self.node_id_counter = itertools.count(0)
        self.depth = 1
        self.size = 1
        self.var_nodes = []

    def duplicate(self, _id: int) -> "Tree":
        ret = Tree(_id)
        # ret.nodes = copy.copy(self.nodes)
        ret.nodes = {}
        for key, val in self.nodes.items():
            if isinstance(val, Hole) or isinstance(val, Node):
                ret.nodes[key] = val.duplicate()
            else:
                ret.nodes[key] = val
        ret.to_children = self.to_children.copy()
        ret.to_parent = self.to_parent.copy()
        ret.node_id_counter = itertools.tee(self.node_id_counter)[1]
        ret.var_nodes = self.var_nodes.copy()
        ret.depth = self.depth
        ret.size = self.size
        return ret

    def __lt__(self, other):
        if self.size == other.size and self.depth == other.depth:
            return self.id < other.id
        if self.size == other.size:
            return self.depth < other.depth
        return self.size < other.size


class Synthesizer:
    """
    Interface for synthesizer with some shared functions.
    """

    def __init__(self, args, client, img_to_environment):
        self.max_synth_depth = args.max_synth_depth
        self.max_prog_depth = args.max_prog_depth
        self.max_faces = args.max_faces
        self.max_rounds = args.max_rounds
        self.client = client
        self.gt_prog_id = 0
        self.logs = []
        self.synthesis_overview = []
        self.img_to_environment = img_to_environment
        self.program_counter = itertools.count(0)
        self.synthesis_overview.append(
            (
                "Ground Truth Program",
                "Extracted Program",
                "Round",
                "# Objects",
                "FTA Construction Time",
                "# Enumerated Programs",
            )
        )

    def get_indices(self, env, gt_prog):
        """
        Given the ground truth program, and the input image, automatically find out which are the labels by running the program on this input
        """
        ids = eval_extractor(gt_prog, env)
        return [env[obj_id]["ObjPosInImgLeftToRight"] for obj_id in ids]

    def get_differing_images(self, prog1, prog2) -> bool:
        """
        Returns the list of images on which 2 programs have different outputs
        """

        print("evaluating program equivalence")
        print("prog1:", prog1)
        print("prog2:", prog2)

        assert len(self.img_to_environment) > 0
        incorrect_img_ids = []

        for img_id, lib in self.img_to_environment.items():

            # env = lib["model_env"] if use_ground_truth else lib["ground_truth"]
            env = lib["ground_truth"]
            ids1 = eval_extractor(prog1, env)
            ids2 = eval_extractor(prog2, env)

            # print("ids1:", ids1)
            # print("ids2:", ids2)

            if ids1 != ids2:
                # print("image id:", img_id)
                incorrect_img_ids.append(img_id)

        print("Programs differ on " + str(len(incorrect_img_ids)) + " images")
        print("Differing images: ", incorrect_img_ids)
        return incorrect_img_ids

    def synthesize_top_down(self, env, eval_cache, args):
        output = {key for (key, details) in env.items()
                  if "ActionApplied" in details}

        output_dict = {}
        output_dict[str(output)] = output
        seen_progs = set()

        tree = Tree(next(self.program_counter))
        tree.nodes[0] = Hole(0, "extr", str(output), str(output))
        tree.var_nodes.append(0)
        worklist = []
        hq.heappush(worklist, tree)
        output_objs_str = get_output_objs(env, Blur())
        num_progs = 0
        progs = []
        prog_threshold = 20 if args.use_active_learning else 1

        while worklist:
            if len(progs) >= prog_threshold:
                print([str(prog) for prog in progs])
                if args.use_active_learning:
                    return progs, num_progs
                else:
                    return progs[0], num_progs
            num_progs += 1
            cur_tree = hq.heappop(worklist)
            prog = construct_prog_from_tree(cur_tree)
            if not get_type(prog):
                continue
            # EQUIVALENCE REDUCTION
            if args.equiv_reduction:
                if output_objs_str and args.partial_eval:
                    should_prune = partial_eval(
                        prog, env, output_dict, eval_cache, True)
                    if should_prune:
                        continue
                if not isinstance(prog, Hole):
                    simplified_prog = simplify(
                        prog.duplicate(), len(env), output_dict)
                    if simplified_prog is None or str(simplified_prog) in seen_progs:
                        continue
                    seen_progs.add(str(simplified_prog))
            if not cur_tree.var_nodes:
                extracted_objs = eval_extractor(
                    prog, env, output_dict=output_dict, eval_cache=eval_cache
                )
                extracted_objs_str = ",".join(sorted(extracted_objs))
                if len(env) == 0 or extracted_objs_str == output_objs_str:
                    progs.append(copy.deepcopy(prog))
                continue
            if num_progs % 1000 == 0:
                print(num_progs)
                print(prog)
                print(len(progs))
                print(cur_tree.size)
                print()
            hole_num = cur_tree.var_nodes.pop(0)
            hole = cur_tree.nodes[hole_num]
            if hole.depth > self.max_synth_depth:
                print("Max depth reached")
                continue
            node_type = cur_tree.nodes[hole_num].node_type
            parent_node = (
                None if hole_num == 0 else cur_tree.nodes[cur_tree.to_parent[hole_num]]
            )
            if node_type == "extr":
                new_sub_extrs = get_extractors(
                    parent_node,
                    output_dict[hole.output_over],
                    output_dict[hole.output_under],
                    env,
                )
            elif node_type == "attr":
                new_sub_extrs = get_attributes(
                    output_dict[hole.output_over], output_dict[hole.output_under]
                )
            elif node_type == "age":
                new_sub_extrs = [(18, [], [], [], 0)]
            elif node_type == "index":
                new_sub_extrs = [
                    (index, [], [], [], 0)
                    for index in get_valid_indices(
                        env,
                        output_dict[hole.output_under],
                        output_dict[hole.output_over],
                    )
                ]
            elif node_type == "word":
                new_sub_extrs = [
                    (word, [], [], [], 0)
                    for word in get_valid_words(
                        env,
                        output_dict[hole.output_under],
                        output_dict[hole.output_over],
                    )
                ]
            elif node_type == "obj":
                new_sub_extrs = [
                    (obj, [], [], [], 0)
                    for obj in get_valid_objects(
                        env,
                        output_dict[hole.output_under],
                        output_dict[hole.output_over],
                    )
                ]
            for (
                sub_extr,
                children,
                child_outputs_over,
                child_outputs_under,
                size,
            ) in new_sub_extrs:
                if isinstance(sub_extr, Node):
                    sub_extr.output_over = str(hole.output_over)
                    sub_extr.output_under = str(hole.output_under)
                prog_output = get_prog_output(sub_extr, env, parent_node)
                # OUTPUT ESTIMATION-BASED PRUNING
                if args.goal_inference:
                    if prog_output and invalid_output(
                        output_dict[hole.output_over],
                        output_dict[hole.output_under],
                        prog_output,
                    ):
                        continue
                new_tree = cur_tree.duplicate(next(self.program_counter))
                new_tree.nodes[hole_num] = sub_extr
                new_tree.size += size
                for child, child_output_over, child_output_under in zip(
                    children, child_outputs_over, child_outputs_under
                ):
                    over_str = str(child_output_over)
                    under_str = str(child_output_under)
                    if over_str not in output_dict:
                        output_dict[over_str] = child_output_over
                    if under_str not in output_dict:
                        output_dict[under_str] = child_output_under
                    new_hole = Hole(hole.depth + 1, child, over_str, under_str)
                    new_tree.depth = max(new_tree.depth, new_hole.depth)
                    new_node_num = len(new_tree.nodes)
                    new_tree.nodes[new_node_num] = new_hole
                    new_tree.var_nodes.append(new_node_num)
                    new_tree.to_parent[new_node_num] = hole_num
                    if hole_num in new_tree.to_children:
                        new_tree.to_children[hole_num].append(new_node_num)
                    else:
                        new_tree.to_children[hole_num] = [new_node_num]
                hq.heappush(worklist, new_tree)
        return None

    def minimax(self, progs, img_to_environment, env_name):
        min_progs = 0
        min_img = None
        finished = True
        for img, env in img_to_environment.items():
            env = env[env_name]
            inds_to_num_progs = {}
            for prog in progs:
                extracted_objs = eval_extractor(
                    prog, env
                )
                extracted_objs_str = ",".join(sorted(extracted_objs))
                if extracted_objs_str in inds_to_num_progs:
                    inds_to_num_progs[extracted_objs_str].append(str(prog))
                else:
                    inds_to_num_progs[extracted_objs_str] = [str(prog)]
            if len(inds_to_num_progs) > 1:
                finished = False
            if min_img is None or min_progs > max(inds_to_num_progs.values(), key=len):
                min_progs = max(inds_to_num_progs.values(), key=len)
                min_img = img
        if finished:
            return True, None, progs[0]
        return False, min_img, None

    def occur_number(self, progs, img_to_environment, env_name):
        skip_these = set()
        for i in range(len(progs)):
            num_indistinguishable = 0
            if i in skip_these:
                continue
            for j in range(i + 1, len(progs)):
                if not self.is_distinguishable(progs[i], progs[j], img_to_environment, env_name):
                    num_indistinguishable += 1
                    skip_these.add(j)
            if num_indistinguishable >= len(progs) * .75:
                return progs[i]
        return None

    def is_distinguishable(self, prog1, prog2, img_to_environment, env_name):
        for _, env in img_to_environment.items():
            env = env[env_name]
            prog1_output = eval_extractor(prog1, env)
            prog1_output_str = ",".join(sorted(prog1_output))
            prog2_output = eval_extractor(prog2, env)
            prog2_output_str = ",".join(sorted(prog2_output))
            if prog1_output_str != prog2_output_str:
                return True
        return False

    def get_challengeable_query(self, rec, progs, img_to_environment, used_imgs, env_name):
        progs_dist_from_rec = [prog for prog in progs if self.is_distinguishable(
            rec, prog, img_to_environment, env_name)]
        for img, env in img_to_environment.items():
            if img in used_imgs:
                continue
            env = env[env_name]
            rec_output = eval_extractor(rec, env)
            if not rec_output:
                continue
            rec_output_str = ",".join(sorted(rec_output))
            num_progs_with_same_output = 0
            for prog in progs_dist_from_rec:
                prog_output = eval_extractor(prog, env)
                prog_output_str = ",".join(sorted(prog_output))
                if rec_output_str == prog_output_str:
                    num_progs_with_same_output += 1
            if num_progs_with_same_output < len(progs) * .25:
                return img
        _, img, _ = self.minimax(progs, img_to_environment, env_name)
        return img

    def annotate_environment(self, indices, img_dir, img_to_environment, env_name, action=Blur()):
        img_index = img_to_environment[img_dir]["img_index"]
        trace = [(img_index, i) for i in indices]
        env = img_to_environment[img_dir][env_name]
        env = {**env, **img_to_environment[img_dir][env_name]}
        for details_map in env.values():
            if "ActionApplied" in details_map:
                del details_map["ActionApplied"]
        for (img_index, index) in trace:
            for details_map in env.values():
                if (
                    details_map["ObjPosInImgLeftToRight"] == index
                    and details_map["ImgIndex"] == img_index
                ):
                    details_map["ActionApplied"] = action
        return env

    def perform_synthesis(
        self,
        args,
        gt_prog=None,
        example_imgs=[],
        testing=True,
    ):
        print("Starting synthesis!")
        print()
        if gt_prog:
            print("Ground truth program: ", gt_prog)
        img_to_environment = self.img_to_environment.copy()
        img_dirs = []
        # assuming one action for now
        action = Blur()
        rounds = 1
        total_synthesis_time = 0
        annotated_env = {}
        img_options = list(img_to_environment.keys())
        while rounds <= self.max_rounds:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(args.time_limit)
            try:
                start_time = time.perf_counter()
                if testing:
                    # Interactive testing
                    if args.interactive:
                        while True:
                            filepath = filedialog.askopenfilename(
                                title="Select an Image",
                                filetypes=(("images", "*.jpg"),
                                           ("all files", "*.*")),
                            )
                            img_dir = filepath.split("ImageEye/")[1]
                            env = img_to_environment[img_dir]["ground_truth"]
                            action_to_objects = annotate_image(img_dir, env)
                            # TODO: (maybe) Support multiple actions?
                            (action, indices) = list(
                                action_to_objects.items())[0]
                            env_name = "ground_truth" if args.use_ground_truth else "model_env"
                            annotated_env = (
                                self.annotate_environment(
                                    indices, img_dir, img_to_environment, env_name, action
                                )
                                | annotated_env
                            )
                            should_continue = input("Add another image? (y/n)")
                            if should_continue == "n":
                                break
                    # Automatically chosen examples using heuristic
                    else:
                        print("Starting round ", rounds)
                        print()
                        img_dir, _ = min(
                            [
                                (img_dir,
                                 img_to_environment[img_dir]["model_env"])
                                for img_dir in img_options
                            ],
                            key=lambda tup: (len(tup[1]), str(tup[0])),
                        )
                        print("New image: ", img_dir)
                        # image is labelled based on ground truth
                        gt_env = img_to_environment[img_dir]["ground_truth"]
                        indices = self.get_indices(gt_env, gt_prog)
                        if rounds == 1 and not indices:
                            img_options.remove(img_dir)
                            continue
                        img_dirs.append(img_dir)
                        env_name = "ground_truth" if args.use_ground_truth else "model_env"
                        annotated_env = (
                            self.annotate_environment(
                                indices, img_dir, img_to_environment, env_name)
                            | annotated_env
                        )
                num_attributes = get_num_attributes(annotated_env)
                construction_start_time = time.perf_counter()
                prog, num_progs = self.synthesize_top_down(
                    annotated_env, {}, args
                )
                print("Program: ", prog)
                construction_end_time = time.perf_counter()
                construction_time = construction_end_time - construction_start_time
                row = (
                    gt_prog,
                    prog,
                    rounds,
                    len(annotated_env),
                    construction_time,
                    num_progs,
                )
                self.synthesis_overview.append(row)
                if args.interactive:
                    print("Finished round ", rounds)
                    print("Synthesized program: ", prog)
                    for img_dir, env in img_to_environment.items():
                        img = cv2.imread(img_dir, 1)
                        edited_img = eval_apply_action(
                            ApplyAction(action, prog),
                            env["ground_truth"],
                            [img],
                        )[0]
                        img_name = img_dir.split("/")[-1]
                        cv2.imwrite("output/" + img_name, edited_img)
                    print("Images written to output directory")
                    response = input("Continue?")
                    if response == "n":
                        break
                    else:
                        continue
                # the list of images where synthesized prog and gt_prog have different outputs
                if testing:
                    img_options = self.get_differing_images(
                        prog, gt_prog)
                else:
                    img_options = []
                # if list is empty, synthesized program is correct
                if not img_options:
                    print("Finished synthesis.")
                    print("Program: ", str(prog))
                    end_time = time.perf_counter()
                    cur_round_time = end_time - start_time
                    total_synthesis_time += cur_round_time
                    print("Number of rounds: ", str(rounds))
                    print("Total Synthesis Time: ", str(total_synthesis_time))
                    return (
                        prog,
                        cur_round_time,
                        rounds,
                        img_dirs,
                        len(annotated_env),
                        num_attributes,
                    )
                if example_imgs:
                    break
                end_time = time.perf_counter()
                cur_round_time = end_time - start_time
                total_synthesis_time += cur_round_time
                rounds += 1
            except TimeOutException:
                end_time = time.perf_counter()
                cur_round_time = end_time - start_time
                print("TIMEOUT")
                return (
                    "TIMEOUT",
                    cur_round_time,
                    rounds,
                    img_dirs,
                    len(annotated_env),
                    num_attributes,
                )
        if args.interactive:
            print("Done!")
            return
        print("Synthesis failed.")
        print(rounds)
        return None, 0, rounds, img_dirs, len(annotated_env), num_attributes

    def perform_synthesis_epssy(
        self,
        args,
        gt_prog=None,
        testing=True,
    ):
        print("Starting synthesis!")
        print()
        if gt_prog:
            print("Ground truth program: ", gt_prog)
        img_to_environment = self.img_to_environment.copy()
        img_dirs = []
        # assuming one action for now
        action = Blur()
        rounds = 1
        total_synthesis_time = 0
        annotated_env = {}
        env_name = "ground_truth" if args.use_ground_truth else "model_env"
        c = 0
        rec = None
        while rounds <= self.max_rounds:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(args.time_limit)
            try:
                start_time = time.perf_counter()
                if testing:
                    print("Starting round ", rounds)
                    print("Recommendation: ", rec)
                    print("c: ", c)
                    print()
                    if rounds > 1:
                        # finished, img_dir, prog = self.minimax(progs, img_to_environment)
                        prog = self.occur_number(
                            progs, img_to_environment, env_name)
                        if prog is not None:
                            print("Finished synthesis.")
                            print("Program: ", str(prog))
                            end_time = time.perf_counter()
                            cur_round_time = end_time - start_time
                            total_synthesis_time += cur_round_time
                            print("Number of rounds: ", str(rounds))
                            print("Total Synthesis Time: ",
                                  str(total_synthesis_time))
                            return (
                                prog,
                                cur_round_time,
                                len(img_dirs),
                                img_dirs,
                                len(annotated_env),
                                "occur number"
                            )
                        img_dir = self.get_challengeable_query(
                            rec, progs, img_to_environment, img_dirs, env_name)
                        print("New image: ", img_dir)
                        # User labels based on ground truth
                        env = img_to_environment[img_dir]["ground_truth"]
                        indices = self.get_indices(env, gt_prog)
                        # if rounds == 1 and not indices:
                        # img_options.remove(img_dir)
                        # continue
                        img_dirs.append(img_dir)
                        annotated_env = (
                            self.annotate_environment(
                                indices, img_dir, img_to_environment, "ground_truth")
                            | annotated_env
                        )
                construction_start_time = time.perf_counter()
                if rounds > 1:
                    rec_output = eval_extractor(rec, env)
                    rec_output_str = ",".join(sorted(rec_output))
                    gt_output = eval_extractor(gt_prog, env)
                    if rec_output_str == ",".join(sorted(gt_output)):
                        c += 1
                    else:
                        c = 0
                    if c >= 3:
                        print("Finished synthesis.")
                        print("Program: ", str(rec))
                        end_time = time.perf_counter()
                        cur_round_time = end_time - start_time
                        total_synthesis_time += cur_round_time
                        print("Number of rounds: ", str(rounds))
                        print("Total Synthesis Time: ",
                              str(total_synthesis_time))
                        return (
                            rec,
                            cur_round_time,
                            len(img_dirs),
                            img_dirs,
                            len(annotated_env),
                            "recommendation"
                        )
                progs, num_progs = self.synthesize_top_down(
                    annotated_env, {}, args)
                if rec is None or c == 0:
                    rec = progs[0]
                if rounds == 1:
                    rounds += 1
                    continue
                construction_end_time = time.perf_counter()
                construction_time = construction_end_time - construction_start_time
                row = (
                    gt_prog,
                    str([str(prog) for prog in progs]),
                    len(img_dirs),
                    len(annotated_env),
                    construction_time,
                    num_progs,
                )
                self.synthesis_overview.append(row)
                end_time = time.perf_counter()
                cur_round_time = end_time - start_time
                total_synthesis_time += cur_round_time
                rounds += 1
            except TimeOutException:
                end_time = time.perf_counter()
                cur_round_time = end_time - start_time
                print("TIMEOUT")
                return (
                    "TIMEOUT",
                    cur_round_time,
                    len(img_dirs),
                    img_dirs,
                    len(annotated_env),
                    "",
                )
        print("Synthesis failed.")
        print(rounds)
        return None, 0, rounds, img_dirs, len(annotated_env), 0


if __name__ == "__main__":

    args = get_args()
    client = get_client()
    img_folder = "example_imgs/"
    img_to_environment = preprocess(img_folder, args.max_faces)
    synth = Synthesizer(args, client, img_to_environment)
    synth.perform_synthesis(
        args,
        gt_prog=None,
        example_imgs=[],
        testing=True,
    )

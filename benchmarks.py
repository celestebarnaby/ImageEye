from dsl import *


class Benchmark:
    def __init__(self, gt_prog, desc, dataset_name, example_imgs=[]):
        self.gt_prog = gt_prog
        self.desc = desc
        self.dataset_name = dataset_name
        self.ast_depth = get_ast_depth(gt_prog)
        self.ast_size = get_ast_size(gt_prog)
        self.example_imgs = example_imgs


def get_ast_depth(prog):
    if isinstance(prog, Union) or isinstance(prog, Intersection):
        return max([get_ast_depth(extr) for extr in prog.extractors]) + 1
    if isinstance(prog, Complement) or isinstance(prog, Map):
        return get_ast_depth(prog.extractor) + 1
    if isinstance(prog, IsFace) or isinstance(prog, IsText) or isinstance(prog, IsPhoneNumber) or isinstance(prog, IsPrice) or isinstance(prog, IsSmiling) or isinstance(prog, EyesOpen) or isinstance(prog, MouthOpen):
        return 2
    else:
        return 3


def get_ast_size(prog):
    if isinstance(prog, Union) or isinstance(prog, Intersection):
        return sum([get_ast_size(extr) for extr in prog.extractors]) + 1
    if isinstance(prog, Complement):
        return get_ast_size(prog.extractor) + 1
    if isinstance(prog, Map):
        if isinstance(prog.position, GetIsContained):
            extra_size = 1
        else:
            extra_size = 2
        return get_ast_size(prog.extractor) + get_ast_size(prog.restriction) + extra_size - 1
    if isinstance(prog, IsFace) or isinstance(prog, IsText) or isinstance(prog, IsPhoneNumber) or isinstance(prog, IsPrice) or isinstance(prog, IsSmiling) or isinstance(prog, EyesOpen) or isinstance(prog, MouthOpen):
        return 2
    else:
        return 3


benchmarks = [
    # Benchmark(
    #     Map(Union([GetFace(34), IsSmiling(), EyesOpen()]),
    #         IsObject("Person"), GetBelow()),
    #     "Bodies of faces that have id 34, are smiling, or have eyes open",
    #     "wedding",
    #     [
    #         "Ana Maria Photography-80.jpg",
    #         "Ana Maria Photography-38.jpg",
    #         "Ana Maria Photography-33.jpg",
    #         "Ana Maria Photography-49.jpg",
    #         "Ana Maria Photography-102.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Union([Map(GetFace(8), IsFace(), GetNext()),
    #           Map(GetFace(8), IsFace(), GetPrev())]),
    #     "Faces to the left and right of face with id 8",
    #     "wedding",
    #     [
    #         "Ana Maria Photography-105.jpg",
    #         "Ana Maria Photography-18.jpg",
    #         "Ana Maria Photography-42.jpg",
    #         "Ana Maria Photography-49.jpg",
    #         "Ana Maria Photography-102.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Union([GetFace(8), Map(GetFace(8), GetFace(34), GetAbove())]),
    #     "Face 8 and face 34 when it is behind face 8",
    #     "wedding",
    #     [
    #         "Ana Maria Photography-105.jpg",
    #         "Ana Maria Photography-18.jpg",
    #         "Ana Maria Photography-42.jpg",
    #         "Ana Maria Photography-49.jpg",
    #         "Ana Maria Photography-102.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Map(IsFace(), IsFace(), GetAbove()),
    #     "All faces in back",
    #     "wedding",
    #     [
    #         "Ana Maria Photography-100.jpg",
    #         "Ana Maria Photography-101.jpg",
    #         "Ana Maria Photography-53.jpg",
    #         "Ana Maria Photography-49.jpg",
    #         "Ana Maria Photography-102.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Intersection([Complement(IsSmiling()), Map(
    #         IsFace(), IsFace(), GetAbove())]),
    #     "All faces in back that are not smiling",
    #     "wedding",
    #     [
    #         "Ana Maria Photography-100.jpg",
    #         "Ana Maria Photography-101.jpg",
    #         "Ana Maria Photography-53.jpg",
    #         "Ana Maria Photography-49.jpg",
    #         "Ana Maria Photography-102.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Intersection([Map(IsFace(), IsFace(), GetNext()),
    #                  Map(IsFace(), IsFace(), GetPrev())]),
    #     "All faces except leftmost and rightmost face",
    #     "wedding",
    #     [
    #         "Ana Maria Photography-68.jpg",
    #         "Ana Maria Photography-40.jpg",
    #         "Ana Maria Photography-102.jpg",
    #         "Ana Maria Photography-53.jpg",
    #         "Ana Maria Photography-2.jpg",
    #     ],
    # ),
    Benchmark(
        Intersection([IsSmiling(), EyesOpen()]),
        "All faces that are smiling and have eyes open",
        "wedding",
        [
            "Ana Maria Photography-80.jpg",
            "Ana Maria Photography-38.jpg",
            "Ana Maria Photography-33.jpg",
            "Ana Maria Photography-49.jpg",
            "Ana Maria Photography-102.jpg",
        ],
    ),
    # Benchmark(
    #     Intersection([IsFace(), Complement(
    #         Intersection([IsSmiling(), EyesOpen()]))]),
    #     "All faces that are not smiling and have eyes open",
    #     "wedding",
    #     [
    #         "Ana Maria Photography-102.jpg",
    #         "Ana Maria Photography-54.jpg",
    #         "Ana Maria Photography-55.jpg",
    #         "Ana Maria Photography-33.jpg",
    #         "Ana Maria Photography-49.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Intersection([IsSmiling(), EyesOpen(), Complement(GetFace(8))]),
    #     "All faces that are smiling and have eyes open, except face 8",
    #     "wedding",
    #     [
    #         "Ana Maria Photography-54.jpg",
    #         "Ana Maria Photography-68.jpg",
    #         "Ana Maria Photography-40.jpg",
    #         "Ana Maria Photography-102.jpg",
    #         "Ana Maria Photography-33.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Union([GetFace(8), GetFace(34)]),
    #     "Face with id 8 or 34",
    #     "wedding",
    #     [
    #         "Ana Maria Photography-52.jpg",
    #         "Ana Maria Photography-42.jpg",
    #         "Ana Maria Photography-66.jpg",
    #         "Ana Maria Photography-49.jpg",
    #         "Ana Maria Photography-102.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Intersection([IsFace(), Complement(GetFace(8))]),
    #     "All faces except face with id 8",
    #     "wedding",
    #     [
    #         "Ana Maria Photography-91.jpg",
    #         "Ana Maria Photography-122.jpg",
    #         "Ana Maria Photography-66.jpg",
    #         "Ana Maria Photography-49.jpg",
    #         "Ana Maria Photography-102.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Union([GetFace(8), Intersection([IsSmiling(), EyesOpen()])]),
    #     "Face with id 8, plus faces that are smiling and have eyes open",
    #     "wedding",
    #     [
    #         "Ana Maria Photography-40.jpg",
    #         "Ana Maria Photography-68.jpg",
    #         "Ana Maria Photography-96.jpg",
    #         "Ana Maria Photography-49.jpg",
    #         "Ana Maria Photography-102.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Map(Map(IsFace(), IsFace(), GetNext()), IsFace(), GetNext()),
    #     "All faces except 2 leftmost faces",
    #     "wedding",
    #     [
    #         "Ana Maria Photography-91.jpg",
    #         "Ana Maria Photography-38.jpg",
    #         "Ana Maria Photography-33.jpg",
    #         "Ana Maria Photography-49.jpg",
    #         "Ana Maria Photography-102.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Union([Intersection([IsFace(), Complement(IsSmiling())]), BelowAge(18)]),
    #     "Faces that are not smiling or are below 18",
    #     "wedding",
    #     [
    #         "Ana Maria Photography-93.jpg",
    #         "Ana Maria Photography-40.jpg",
    #         "Ana Maria Photography-54.jpg",
    #         "Ana Maria Photography-49.jpg",
    #         "Ana Maria Photography-102.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Union([Map(GetFace(8), IsFace(), GetNext()), GetFace(8)]),
    #     "Face with id 8 and face directly to their right",
    #     "wedding",
    #     [
    #         "Ana Maria Photography-68.jpg",
    #         "Ana Maria Photography-73.jpg",
    #         "Ana Maria Photography-102.jpg",
    #         "Ana Maria Photography-91.jpg",
    #         "Ana Maria Photography-40.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Union([Map(GetFace(8), IsFace(), GetNext()), Map(
    #         GetFace(8), IsFace(), GetPrev()), GetFace(8)]),
    #     "Face with id 8 and faces directly to their left and right",
    #     "wedding",
    #     [
    #         "Ana Maria Photography-105.jpg",
    #         "Ana Maria Photography-18.jpg",
    #         "Ana Maria Photography-42.jpg",
    #         "Ana Maria Photography-49.jpg",
    #         "Ana Maria Photography-102.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Map(MatchesWord("TOTAL"), IsText(), GetRight()),
    #     'Text to the right of the word "TOTAL"',
    #     "receipts2",
    #     [
    #         "33336502_4cf532b827_c.jpg",
    #         "1163818732_f65305d3c7_o.jpg",
    #         "231578268_e5a7d59d28_c.jpg",
    #         "5408339252_de3bdefb47_c.jpg",
    #         "15481556111_4d3150b8cc_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Map(Map(MatchesWord("TOTAL"), IsPrice(), GetRight()), IsPrice(), GetAbove()),
    #     'Price that is above the total price',
    #     "receipts2",
    #     [
    #         "33336502_4cf532b827_c.jpg",
    #         "3524826306_f7995086e0_c.jpg",
    #         "231578268_e5a7d59d28_c.jpg",
    #         "5408339252_de3bdefb47_c.jpg",
    #         "15481556111_4d3150b8cc_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Complement(
    #         Map(Map(IsText(), IsText(), GetAbove()), IsText(), GetAbove())),
    #     "Bottom two columns of text",
    #     "receipts2",
    #     [
    #         "33336502_4cf532b827_c.jpg",
    #         "64253187_429175fba8_c.jpg",
    #         "3884400699_58fdb3781f_c.jpg",
    #         "5408339252_de3bdefb47_c.jpg",
    #         "15481556111_4d3150b8cc_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Intersection([IsText(), Complement(
    #         Union([MatchesWord("total"), IsPrice()]))]),
    #     "All text except prices and the word 'total'",
    #     "receipts2",
    #     [
    #         "33336502_4cf532b827_c.jpg",
    #         "64253187_429175fba8_c.jpg",
    #         "3884400699_58fdb3781f_c.jpg",
    #         "5408339252_de3bdefb47_c.jpg",
    #         "15481556111_4d3150b8cc_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Map(MatchesWord("TOTAL"), IsPrice(), GetRight()),
    #     'Prices to the right of the word "TOTAL"',
    #     "receipts2",
    #     [
    #         "33336502_4cf532b827_c.jpg",
    #         "3524826306_f7995086e0_c.jpg",
    #         "231578268_e5a7d59d28_c.jpg",
    #         "5408339252_de3bdefb47_c.jpg",
    #         "15481556111_4d3150b8cc_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Map(MatchesWord("tax"), IsText(), GetAbove()),
    #     'Text above the word "tax"',
    #     "receipts2",
    #     [
    #         "33336502_4cf532b827_c.jpg",
    #         "3524826306_f7995086e0_c.jpg",
    #         "231578268_e5a7d59d28_c.jpg",
    #         "5408339252_de3bdefb47_c.jpg",
    #         "15481556111_4d3150b8cc_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Union([IsPrice(), IsPhoneNumber()]),
    #     "All prices and all phone numbers",
    #     "receipts2",
    #     [
    #         "9219563622_90355ebf0a_c.jpg",
    #         "33336502_4cf532b827_c.jpg",
    #         "231578268_e5a7d59d28_c.jpg",
    #         "5408339252_de3bdefb47_c.jpg",
    #         "15481556111_4d3150b8cc_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Intersection([IsText(), Complement(IsPrice())]),
    #     "All text that is not a price",
    #     "receipts2",
    #     [
    #         "33336502_4cf532b827_c.jpg",
    #         "64253187_429175fba8_c.jpg",
    #         "3884400699_58fdb3781f_c.jpg",
    #         "5408339252_de3bdefb47_c.jpg",
    #         "15481556111_4d3150b8cc_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Union([Map(MatchesWord("TOTAL"), IsText(), GetRight()),
    #           Map(MatchesWord("SUBTOTAL"), IsText(), GetRight())]),
    #     'Text to the right of the word "TOTAL" or the word "SUBTOTAL"',
    #     "receipts2",
    #     [
    #         "64253187_429175fba8_c.jpg",
    #         "33336502_4cf532b827_c.jpg",
    #         "1163818732_f65305d3c7_o.jpg",
    #         "3884400699_58fdb3781f_c.jpg",
    #         "5408339252_de3bdefb47_c.jpg",
    #         "15481556111_4d3150b8cc_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Map(IsPrice(), IsText(), GetLeft()),
    #     "Text to the left of a price",
    #     "receipts2",
    #     [
    #         "33336502_4cf532b827_c.jpg",
    #         "64253187_429175fba8_c.jpg",
    #         "3884400699_58fdb3781f_c.jpg",
    #         "5408339252_de3bdefb47_c.jpg",
    #         "15481556111_4d3150b8cc_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Intersection([IsText(), Complement(
    #         Union([IsPrice(), IsPhoneNumber()]))]),
    #     "All text that is not a price or phone number",
    #     "receipts2",
    #     [
    #         "64253187_429175fba8_c.jpg",
    #         "33336502_4cf532b827_c.jpg",
    #         "3884400699_58fdb3781f_c.jpg",
    #         "5408339252_de3bdefb47_c.jpg",
    #         "15481556111_4d3150b8cc_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Intersection([IsPrice(), Complement(
    #         Map(MatchesWord("TOTAL"), IsText(), GetRight()))]),
    #     'Text that is a price and is not to the right of the word "TOTAL"',
    #     "receipts2",
    #     [
    #         "64253187_429175fba8_c.jpg",
    #         "13525448153_38a6b57049_c.jpg",
    #         "3884400699_58fdb3781f_c.jpg",
    #         "5408339252_de3bdefb47_c.jpg",
    #         "15481556111_4d3150b8cc_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Map(Map(IsText(), IsText(), GetLeft()), IsText(), GetLeft()),
    #     "All text except two leftmost columns",
    #     "receipts2",
    #     [
    #         "33449180_0a09305667_c.jpg",
    #         "64253187_429175fba8_c.jpg",
    #         "3884400699_58fdb3781f_c.jpg",
    #         "5408339252_de3bdefb47_c.jpg",
    #         "15481556111_4d3150b8cc_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Union([IsObject("Car"), IsObject("Bicycle")]),
    #     "All cars and bicycles",
    #     "cars",
    #     [
    #         "9107010_479657625c_o.jpg",
    #         "5421932595_68f7ab545d_c.jpg",
    #         "5648671688_8b85d9af12_c.jpg",
    #         "6708503525_870ea33fd2_c.jpg",
    #         "7051526761_7f1293207a_k.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Map(MatchesWord("319"), IsObject("Car"), GetIsContained()),
    #     " Car with number 319",
    #     "cars",
    #     [
    #         "n02958343_9005.JPEG",
    #         "car1.jpeg",
    #         "5648671688_8b85d9af12_c.jpg",
    #         "6708503525_870ea33fd2_c.jpg",
    #         "7051526761_7f1293207a_k.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Map(IsObject("Car"), IsFace(), GetContains()),
    #     "All faces within car",
    #     "cars",
    #     [
    #         "7051526761_7f1293207a_k.jpg",
    #         "7277639906_2f455d0a66_c.jpg",
    #         "7283056644_e9ca3877d1_c.jpg",
    #         "15598753673_331ea65b54_c.jpg",
    #         "44929498572_0b602cb182_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Complement(IsObject("Car")),
    #     "All objects except cars",
    #     "cars",
    #     [
    #         "9107010_479657625c_o.jpg",
    #         "5421932595_68f7ab545d_c.jpg",
    #         "5648671688_8b85d9af12_c.jpg",
    #         "6708503525_870ea33fd2_c.jpg",
    #         "7051526761_7f1293207a_k.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Complement(Union([IsObject("Car"), IsObject("Bicycle")])),
    #     "All objects except cars and bicycles",
    #     "cars",
    #     [
    #         "38173050612_88886a495d_c.jpg",
    #         "41195542880_7166141ab7_c.jpg",
    #         "7283056644_e9ca3877d1_c.jpg",
    #         "44015278360_ae3fb72419_c.jpg",
    #         "44929498572_0b602cb182_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Map(IsObject("Car"), IsText(), GetContains()),
    #     "All text on a car",
    #     "cars",
    #     [
    #         "7283056644_e9ca3877d1_c.jpg",
    #         "car1.jpeg",
    #         "5648671688_8b85d9af12_c.jpg",
    #         "6708503525_870ea33fd2_c.jpg",
    #         "7051526761_7f1293207a_k.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Intersection([IsText(), Complement(
    #         Map(IsObject("Car"), IsText(), GetContains()))]),
    #     "All text not on a car",
    #     "cars",
    #     [
    #         "n02958343_1902.JPEG",
    #         "n02958343_3671.JPEG",
    #         "n02958343_4294.JPEG",
    #         "n02958343_4588.JPEG",
    #         "n02958343_9005.JPEG",
    #     ],
    # ),
    # Benchmark(
    #     Map(IsText(), IsObject("Car"), GetIsContained()),
    #     "Cars with text on them",
    #     "cars",
    #     [
    #         "car1.jpeg",
    #         "37990571714_16dc487280_c.jpg",
    #         "44929498572_0b602cb182_c.jpg",
    #         "38003299455_d6d697ee64_c.jpg",
    #         "n02958343_4588.JPEG",
    #     ],
    # ),
    # Benchmark(
    #     Map(IsObject("Person"), IsObject("Bicycle"), GetBelow()),
    #     "Bicycles that are being ridden",
    #     "cars",
    #     [
    #         "42957663251_025fb32ac8_c.jpg",
    #         "n02834778_4305.JPEG",
    #         "n02834778_63.JPEG",
    #         "n02834778_1127.JPEG",
    #         "n02834778_2263.JPEG",
    #     ],
    # ),
    # Benchmark(
    #     Intersection([IsObject("Bicycle"), Complement(
    #         Map(IsObject("Person"), IsObject("Bicycle"), GetBelow()))]),
    #     "Bicycles that are not being ridden",
    #     "cars",
    #     [
    #         "42957663251_025fb32ac8_c.jpg",
    #         "14439655154_4598f22beb_c.jpg",
    #         "n02834778_63.JPEG",
    #         "n02834778_1127.JPEG",
    #         "n02834778_2263.JPEG",
    #     ],
    # ),
    # Benchmark(
    #     Intersection([IsObject("Bicycle"), Complement(
    #         Map(BelowAge(18), IsObject("Bicycle"), GetBelow()))]),
    #     "Bicycles that are not being ridden by a child",
    #     "cars",
    #     [
    #         "42957663251_025fb32ac8_c.jpg",
    #         "14439655154_4598f22beb_c.jpg",
    #         "n02834778_1724.JPEG",
    #         "n02834778_1127.JPEG",
    #         "n02834778_2263.JPEG",
    #     ],
    # ),
    # Benchmark(
    #     Union([IsObject("Bicycle"), IsObject("Car"), IsObject("Person")]),
    #     "All bicycles, cars, and people",
    #     "cars",
    #     [
    #         "37990571714_16dc487280_c.jpg",
    #         "38003299455_d6d697ee64_c.jpg",
    #         "n02834778_1724.JPEG",
    #         "n02834778_1127.JPEG",
    #         "n02834778_2263.JPEG",
    #     ],
    # ),
    # Benchmark(
    #     Map(IsObject("Bicycle"), BelowAge(18), GetAbove()),
    #     "All kids on a bicycle",
    #     "cars",
    #     [
    #         "3831788270_a1b83f4774_c.jpg",
    #         "n02834778_1724.JPEG",
    #         "24979416792_a9c2e9e3e2_c.jpg",
    #         "44929498572_0b602cb182_c.jpg",
    #         "n02834778_2263.JPEG",
    #     ],
    # ),
    # Benchmark(
    #     Intersection([IsFace(), Complement(
    #         Map(IsObject("Bicycle"), IsFace(), GetAbove()))]),
    #     "Faces of people not riding bicycles",
    #     "cars",
    #     [
    #         "42957663251_025fb32ac8_c.jpg",
    #         "14439655154_4598f22beb_c.jpg",
    #         "n02834778_63.JPEG",
    #         "n02834778_1127.JPEG",
    #         "n02834778_2263.JPEG",
    #     ],
    # ),
    # Benchmark(
    #     Union([IsObject("Cat"), IsFace()]),
    #     "All cats and human faces",
    #     "cats",
    #     [
    #         "n02121808_111.JPEG",
    #         "n02121808_1451.JPEG",
    #         "n02121808_246.JPEG",
    #         "n02121808_133.JPEG",
    #         "n02121808_3908.JPEG",
    #     ],
    # ),
    # Benchmark(
    #     Union([IsObject("Cat"), EyesOpen()]),
    #     "All cats and faces with eyes open",
    #     "cats",
    #     [
    #         "n02121808_111.JPEG",
    #         "n02121808_1451.JPEG",
    #         "n02121808_246.JPEG",
    #         "n02121808_133.JPEG",
    #         "n02121808_3908.JPEG",
    #     ],
    # ),
    # Benchmark(
    #     Intersection([IsObject("Cat"), Complement(
    #         Map(IsObject("Cat"), IsObject("Cat"), GetBelow()))]),
    #     "Topmost cat",
    #     "cats",
    #     [
    #         "n02121808_52.JPEG",
    #         "n02121808_14.JPEG",
    #         "n02121808_246.JPEG",
    #         "n02121808_133.JPEG",
    #         "n02121808_3908.JPEG",
    #     ],
    # ),
    # Benchmark(
    #     Intersection(
    #         [
    #             Map(IsObject("Cat"), IsObject("Cat"), GetNext()),
    #             Map(IsObject("Cat"), IsObject("Cat"), GetPrev()),
    #         ]
    #     ),
    #     "Cats that are between two other cats",
    #     "cats",
    #     [
    #         "n02121808_16252.JPEG",
    #         "n02121808_14.JPEG",
    #         "n02121808_246.JPEG",
    #         "n02121808_133.JPEG",
    #         "n02121808_3908.JPEG",
    #     ],
    # ),
    # Benchmark(
    #     Map(IsObject("Guitar"), IsFace(), GetAbove()),
    #     "People playing guitar",
    #     "guitars",
    #     [
    #         "35138463884_d6e585ec6f_c.jpg",
    #         "2559459918_22441e06e6_c.jpg",
    #         "173177904_4033f5d57a_z.jpg",
    #         "207443806_9f7c547646_c.jpg",
    #         "325813428_db3474fe2f_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Union([IsObject("Guitar"), Map(IsObject("Guitar"), IsFace(), GetAbove())]),
    #     "Guitars and people playing guitar",
    #     "guitars",
    #     [
    #         "35138463884_d6e585ec6f_c.jpg",
    #         "2559459918_22441e06e6_c.jpg",
    #         "47662639582_34f9ae09fe_c.jpg",
    #         "207443806_9f7c547646_c.jpg",
    #         "325813428_db3474fe2f_c.jpg",
    #     ],
    # ),
    # Benchmark(
    #     Intersection([IsFace(), Complement(
    #         Map(IsObject("Guitar"), IsFace(), GetAbove()))]),
    #     "Faces of people not playing guitar",
    #     "guitars",
    #     [
    #         "6176795637_c6ff252d4a_c.jpg",
    #         "2729314473_4272a55d86_c.jpg",
    #         "2982619528_a19341718f_c.jpg",
    #         "35138463884_d6e585ec6f_c.jpg",
    #         "325813428_db3474fe2f_c.jpg",
    #     ],
    # ),
]

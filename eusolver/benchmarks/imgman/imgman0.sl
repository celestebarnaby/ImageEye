
(set-logic IMG)

(synth-fun f ((input Imgs)) Imgs
    ((Start Imgs ((Match input StartStr)
                (Union Start Start)
                (Intersection Start Start)
                (Complement input Start)
                (Find input Start StartStr Pos)
                ))
    (StartStr String (
        "EyesOpen"
	"Index104"
	"Index136"
	"Index34"
	"Index37"
	"Index553"
	"Index78"
	"Index79"
	"Index8"
	"Index83"
	"MouthOpen"
	"NameGlasses"
	"NamePerson"
	"NameSuit"
	"NameWedding Gown"
	"Smile"
	"Text0"
	"TypeFace"
	"TypeText"
        ))
    (Pos String (
        "GetLeft"
        "GetRight"
        "GetAbove"
        "GetBelow"
        "GetParents"
        "GetChildren"
        "GetNext"
        "GetPrev"))))

(declare-var s0 Set)

(constraint (= (f {{EyesOpen Index104 TypeFace bb: 666 821 292 481 14}, {EyesOpen Index136 TypeFace bb: 1397 1454 384 452 14}, {EyesOpen Index78 TypeFace bb: 541 676 433 621 8}, {Index34 MouthOpen EyesOpen Smile TypeFace bb: 1024 1087 575 650 104}, {Index37 MouthOpen EyesOpen Smile TypeFace bb: 573 672 483 601 56}, {Index37 Smile TypeFace MouthOpen bb: 776 862 420 548 22}, {Index553 TypeFace bb: 688 734 478 601 119}, {Index79 TypeFace bb: 687 750 556 633 8}, {Index8 MouthOpen EyesOpen Smile TypeFace bb: 350 422 583 672 119}, {Index8 MouthOpen EyesOpen Smile TypeFace bb: 461 558 455 577 56}, {Index8 MouthOpen EyesOpen Smile TypeFace bb: 881 1032 271 449 14}, {Index8 Smile TypeFace MouthOpen bb: 1338 1407 610 685 104}, {Index8 TypeFace bb: 455 574 645 838 105}, {MouthOpen EyesOpen Smile TypeFace Index83 bb: 379 457 320 420 104}, {NameGlasses bb: 665 840 336 397 14}, {NamePerson bb: 0 120 563 1018 8}, {NamePerson bb: 1099 1588 114 1051 8}, {NamePerson bb: 1239 1504 588 985 104}, {NamePerson bb: 1285 1522 332 818 14}, {NamePerson bb: 143 630 553 1476 119}, {NamePerson bb: 448 895 239 1066 14}, {NamePerson bb: 456 958 414 1566 119}, {NamePerson bb: 638 989 378 1054 22}, {NamePerson bb: 644 769 533 692 8}, {NamePerson bb: 802 1308 220 1022 14}, {NamePerson bb: 946 1175 552 829 104}, {NameSuit bb: 251 556 392 1054 104}, {NameWedding Gown bb: 262 1037 644 1598 105}, {NameWedding Gown bb: 31 957 506 1598 56}, {TypeFace Index34 bb: 775 912 342 544 8}, {TypeText Text0 bb: 1112 1149 385 415 104}} ) {{Index34 MouthOpen EyesOpen Smile TypeFace bb: 1024 1087 575 650 104}, {Index8 MouthOpen EyesOpen Smile TypeFace bb: 881 1032 271 449 14}, {Index79 TypeFace bb: 687 750 556 633 8}} ))

(check-synth)
                
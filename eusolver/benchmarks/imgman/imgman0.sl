
(set-logic IMG)

(synth-fun f ((input Imgs)) Imgs
    ((Start Imgs ((Match input StartStr)
                (Union Start Start)
                (Intersection Start Start)
                (Complement input Start)
                (Find input Start StartStr Pos)
                ))
    (StartStr String (
        "BelowAge18"
	"EyesOpen"
	"Index111"
	"Index166"
	"Index17"
	"Index18"
	"Index229"
	"Index30"
	"Index32"
	"Index34"
	"Index37"
	"Index7"
	"Index78"
	"Index79"
	"Index8"
	"MouthOpen"
	"NamePerson"
	"NameTie"
	"Smile"
	"TypeFace"
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

(constraint (= (f {{Index17 TypeFace EyesOpen bb: 620 787 306 523 42}, {Index30 TypeFace EyesOpen Smile bb: 393 544 581 773 97}, {Index34 TypeFace bb: 1097 1161 202 292 118}, {Index34 TypeFace bb: 775 912 342 544 8}, {Index37 TypeFace MouthOpen Smile bb: 645 777 659 833 97}, {Index37 TypeFace Smile MouthOpen EyesOpen bb: 1055 1158 455 586 63}, {Index78 TypeFace EyesOpen bb: 541 676 433 621 8}, {Index79 TypeFace bb: 687 750 556 633 8}, {Index8 TypeFace BelowAge18 EyesOpen bb: 584 626 291 363 118}, {Index8 TypeFace Smile MouthOpen EyesOpen bb: 819 929 445 579 63}, {NamePerson bb: 0 120 563 1018 8}, {NamePerson bb: 1093 1495 365 1031 63}, {NamePerson bb: 1099 1588 114 1051 8}, {NamePerson bb: 161 538 362 1043 63}, {NamePerson bb: 175 633 501 1590 97}, {NamePerson bb: 316 878 241 1044 118}, {NamePerson bb: 331 879 243 1048 42}, {NamePerson bb: 412 992 366 1060 83}, {NamePerson bb: 488 756 438 831 63}, {NamePerson bb: 540 875 624 1585 97}, {NamePerson bb: 644 769 533 692 8}, {NamePerson bb: 720 1042 400 990 63}, {NamePerson bb: 733 1087 375 1064 24}, {NamePerson bb: 765 1396 142 1054 42}, {NamePerson bb: 846 1097 487 1043 83}, {NamePerson bb: 857 1264 165 1011 118}, {NamePerson bb: 958 1349 261 1056 24}, {NamePerson bb: 996 1271 408 1010 63}, {NameTie bb: 459 543 808 1081 97}, {TypeFace Index111 Smile MouthOpen EyesOpen bb: 598 703 479 616 63}, {TypeFace Index229 bb: 1041 1143 324 454 24}, {TypeFace Index7 MouthOpen Smile bb: 1260 1369 397 536 63}, {TypeFace Smile Index18 MouthOpen EyesOpen bb: 853 1064 221 480 42}, {TypeFace Smile MouthOpen EyesOpen Index166 bb: 386 495 397 534 63}, {TypeFace Smile MouthOpen EyesOpen Index32 bb: 743 863 421 589 83}, {TypeFace Smile MouthOpen EyesOpen Index32 bb: 821 889 500 624 83}} ) {{NamePerson bb: 644 769 533 692 8}, {NamePerson bb: 540 875 624 1585 97}, {NamePerson bb: 331 879 243 1048 42}, {NamePerson bb: 996 1271 408 1010 63}, {NamePerson bb: 488 756 438 831 63}, {NamePerson bb: 846 1097 487 1043 83}} ))

(check-synth)
                
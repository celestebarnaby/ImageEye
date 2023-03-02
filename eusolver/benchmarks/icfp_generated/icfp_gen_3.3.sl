(set-logic BV)

(define-fun shr1 ((x (BitVec 64))) (BitVec 64) (bvlshr x #x0000000000000001))
(define-fun shr4 ((x (BitVec 64))) (BitVec 64) (bvlshr x #x0000000000000004))
(define-fun shr16 ((x (BitVec 64))) (BitVec 64) (bvlshr x #x0000000000000010))
(define-fun shl1 ((x (BitVec 64))) (BitVec 64) (bvshl x #x0000000000000001))
(define-fun if0 ((x (BitVec 64)) (y (BitVec 64)) (z (BitVec 64))) (BitVec 64) (ite (= x #x0000000000000001) y z))

(synth-fun f ( (x (BitVec 64))) (BitVec 64)
(

(Start (BitVec 64) (#x0000000000000000 #x0000000000000001 x (bvnot Start)
                    (shl1 Start)
 		    (shr1 Start)
		    (shr4 Start)
		    (shr16 Start)
		    (bvand Start Start)
		    (bvor Start Start)
		    (bvxor Start Start)
		    (bvadd Start Start)
		    (if0 Start Start Start)
 ))
)
)
(constraint (= (f #x385AAE170AA67A0E) #x70B55C2E154CF41D))
(constraint (= (f #xBDFC0554D76E9B24) #x7BF80AA9AEDD3649))
(constraint (= (f #x7636B15935025367) #xEC6D62B26A04A6CF))
(constraint (= (f #xE2518F197C7AC95F) #xC4A31E32F8F592BF))
(constraint (= (f #x1B412DE3726A06BA) #x36825BC6E4D40D75))
(constraint (= (f #x92A5092429504AA9) #x92A5092429504AA9))
(constraint (= (f #xA94554288A82A945) #xA94554288A82A945))
(constraint (= (f #x82AA954928042221) #x82AA954928042221))
(constraint (= (f #x82A0A448A5285411) #x82A0A448A5285411))
(constraint (= (f #x455252A92A2454A5) #x455252A92A2454A5))
(constraint (= (f #x68BF0EBB92F1ED90) #x90B50058B3DEF396))
(constraint (= (f #xBA87933526EB5BCC) #x39CFF39786A5EE77))
(constraint (= (f #x844D37C37D8FAEA4) #x736DF4C04A975671))
(constraint (= (f #x8232852382AD692C) #x75AA528A4527C041))
(constraint (= (f #xA7B8F6A7F623D834) #x4DCB79ED8A79EA48))
(constraint (= (f #x140B50532FA74FDD) #x2816A0A65F4E9FBB))
(constraint (= (f #xCEAC9372181D91F7) #x9D5926E4303B23EF))
(constraint (= (f #x6EC2E38A8B13CF9D) #xDD85C71516279F3B))
(constraint (= (f #x482C273D542D165D) #x90584E7AA85A2CBB))
(constraint (= (f #xF0C515FE526FB559) #xE18A2BFCA4DF6AB3))
(constraint (= (f #x2226666666667776) #x444CCCCCCCCCEEED))
(constraint (= (f #x088888888AAAEEFE) #x111111111555DDFD))
(constraint (= (f #x0222222222223332) #x0444444444446665))
(constraint (= (f #x000008888888BFFE) #x0000111111117FFD))
(constraint (= (f #x08888888AAAABBBA) #x1111111155557775))
(constraint (= (f #x42A254A522512A95) #x42A254A522512A95))
(constraint (= (f #x8142A92942514295) #x8142A92942514295))
(constraint (= (f #x80A8411154511155) #x80A8411154511155))
(constraint (= (f #x401244A0A2510A55) #x401244A0A2510A55))
(constraint (= (f #x8514AA40AA255555) #x8514AA40AA255555))
(constraint (= (f #x000088DDDDDDDDFE) #xFFFF772219944424))
(constraint (= (f #xAAAABBBBBBBBBFFE) #x5555399998888446))
(constraint (= (f #x22222333333337FE) #xDDDDDAAAAA9994CE))
(constraint (= (f #x8888999DDDDDDFFE) #x77775DD998884224))
(constraint (= (f #x133333333333377E) #xECCCCB999999954E))
(check-synth)

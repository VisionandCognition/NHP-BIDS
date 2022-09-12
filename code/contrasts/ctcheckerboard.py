# CT-Shaped Checkeboard event names and contrasts
# event_names = [
#     'GapR', 'GapDR', 'GapUR', 'CurveSegR',
#     'CurveSegDR', 'CurveSegUR', 'CircleDR', 'CircleUR',
#     'GapL', 'GapDL', 'GapUL', 'CurveSegL',
#     'CurveSegDL', 'CurveSegUL', 'CircleDL', 'CircleUR',
#     'Reward',
# ]
# The order of the contrasts are:
# * From eccentric to foveal
# * Bottom before top visual field
# * Left before right visual field
contrasts = [
    # --------------------------- Targets (Circles) --------------------------
    ['CircleDL>R', 'T',  # t-test
     ['CircleDL',  # >                      Contrast 0: Target - Down-Left
      'GapR', 'GapDR', 'GapUR', 'CurveSegR',
      'CurveSegDR', 'CurveSegUR', 'CircleDR', 'CircleUR',
      ],
     [8.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]],

    ['CircleDR>L', 'T',  # t-test
     ['CircleDR',  # >                      Contrast 1: Target - Down-Right
      'GapL', 'GapDL', 'GapUL', 'CurveSegL',
      'CurveSegDL', 'CurveSegUL', 'CircleDL', 'CircleUL',
      ],
     [8.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]],

    ['CircleUL>R', 'T',  # t-test
     ['CircleUL',  # >                      Contrast 2: Target - Up-Left
      'GapR', 'GapDR', 'GapUR', 'CurveSegR',
      'CurveSegDR', 'CurveSegUR', 'CircleDR', 'CircleUR',
      ],
     [8.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]],

    ['CircleUR>L', 'T',  # t-test
     ['CircleUR',  # >                      Contrast 3: Target - Up-Right
      'GapL', 'GapDL', 'GapUL', 'CurveSegL',
      'CurveSegDL', 'CurveSegUL', 'CircleDL', 'CircleUL',
      ],
     [8.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]],

    # --------------------------  Peripheral curves  -------------------------
    ['CurveSegDL>R', 'T',  # t-test
     ['CurveSegDL',  # >                    Contrast 4: CurveSegDL - Down-Left
      'GapR', 'GapDR', 'GapUR', 'CurveSegR',
      'CurveSegDR', 'CurveSegUR', 'CircleDR', 'CircleUR',
      ],
     [8.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]],

    ['CurveSegDR>L', 'T',  # t-test
     ['CurveSegDR',  # >                    Contrast 5: CurveSegDR - Down-Right
      'GapL', 'GapDL', 'GapUL', 'CurveSegL',
      'CurveSegDL', 'CurveSegUL', 'CircleDL', 'CircleUL',
      ],
     [8.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]],

    ['CurveSegUL>R', 'T',  # t-test
     ['CurveSegUL',  # >                    Contrast 6: CurveSegUL - Up-Left
      'GapR', 'GapDR', 'GapUR', 'CurveSegR',
      'CurveSegDR', 'CurveSegUR', 'CircleDR', 'CircleUR',
      ],
     [8.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]],

    ['CurveSegUR>L', 'T',  # t-test
     ['CurveSegUR',  # >                    Contrast 7: CurveSegUR - Up-Right
      'GapL', 'GapDL', 'GapUL', 'CurveSegL',
      'CurveSegDL', 'CurveSegUL', 'CircleDL', 'CircleUL',
      ],
     [8.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]],

    # --------------------  Peripheral joints / gaps  --------------------
    ['GapDL>R', 'T',  # t-test
     ['GapDL',  # >                         Contrast 8: Joint Down-Left
      'GapR', 'GapDR', 'GapUR', 'CurveSegR',
      'CurveSegDR', 'CurveSegUR', 'CircleDR', 'CircleUR',
      ],
     [8.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]],

    ['GapDR>L', 'T',  # t-test
     ['GapDR',  # >                         Contrast 9: Joint Down-Right
      'GapL', 'GapDL', 'GapUL', 'CurveSegL',
      'CurveSegDL', 'CurveSegUL', 'CircleDL', 'CircleUL',
      ],
     [8.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]],

    ['GapUL>R', 'T',  # t-test
     ['GapUL',  # >                         Contrast 10: Joint Up-Left
      'GapR', 'GapDR', 'GapUR', 'CurveSegR',
      'CurveSegDR', 'CurveSegUR', 'CircleDR', 'CircleUR',
      ],
     [8.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]],

    ['GapUR>L', 'T',  # t-test
     ['GapUR',  # >                         Contrast 11: Joint Up-Right
      'GapL', 'GapDL', 'GapUL', 'CurveSegL',
      'CurveSegDL', 'CurveSegUL', 'CircleDL', 'CircleUL',
      ],
     [8.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]],

    # --------------------------  Inner curves  --------------------------
    ['CurveSegL>R', 'T',  # t-test
     ['CurveSegL',  # >                     Contrast 12: Curve Left
      'GapR', 'GapDR', 'GapUR', 'CurveSegR',
      'CurveSegDR', 'CurveSegUR', 'CircleDR', 'CircleUR',
      ],
     [8.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]],

    ['CurveSegR>L', 'T',  # t-test
     ['CurveSegR',  # >                     Contrast 13: Curve Right
      'GapL', 'GapDL', 'GapUL', 'CurveSegL',
      'CurveSegDL', 'CurveSegUL', 'CircleDL', 'CircleUL',
      ],
     [8.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]],

    # -----------------------  Inner joints / gaps  -----------------------

    ['GapL>R', 'T',  # t-test
     ['GapL',  # >                          Contrast 14: Joint Left
      'GapR', 'GapDR', 'GapUR', 'CurveSegR',
      'CurveSegDR', 'CurveSegUR', 'CircleDR', 'CircleUR',
      ],
     [8.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]],
    ['GapR>L', 'T',  # t-test
     ['GapR',  # >                          Contrast 15: Joint Right
      'GapL', 'GapDL', 'GapUL', 'CurveSegL',
      'CurveSegDL', 'CurveSegUL', 'CircleDL', 'CircleUL',
      ],
     [8.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]],

    # -----------------------  Reward  -----------------------
    ['Reward>Baseline', 'T',  # t-test
     ['Reward'],  # >                       Contrast 16: Reward
     [1.0]],
]

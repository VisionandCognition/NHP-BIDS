# Curve tracing contrasts
contrasts = [
    ['Curves>Baseline', 'T',  # t-test
     ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR',
      'AttendCenter_COR'],
     [1.0/5]*5],
    ['AttendLeft>AttendRight', 'T',  # t-test
     ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR'],
     [1.0, 1.0, -1.0, -1.0]],
    ['AttendRight>AttendLeft', 'T',  # t-test
     ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR'],
     [-1.0, -1.0, 1.0, 1.0]],
    ['AttendUL>AttendOther', 'T',  # t-test
     ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR'],
     [3.0, -1.0, -1.0, -1.0]],
    ['AttendDL>AttendOther', 'T',  # t-test
     ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR'],
     [-1.0, 3.0, -1.0, -1.0]],
    ['AttendUR>AttendOther', 'T',  # t-test
     ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR'],
     [-1.0, -1.0, 3.0, -1.0]],
    ['AttendDR>AttendOther', 'T',  # t-test
     ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR'],
     [-1.0, -1.0, -1.0, 3.0]],
    ['HandLeft>HandRight', 'T',  # t-test
     ['HandLeft', 'HandRight'],
     [1.0, -1.0]],
    ['HandRight>HandLeft', 'T',  # t-test
     ['HandLeft', 'HandRight'],
     [-1.0, 1.0]],
    ['Reward>Baseline', 'T',  # t-test
     ['Reward'],
     [1.0]],
]


#   0   All Curves > Base
#   1   Attend Left > Attend Right
#   2   Attend Right > Attend Left
#   3   UL > other
#   4   DL > other
#   5   UR > other
#   6   DR > other
#   7   Hand Left > Hand Right
#   8   Hand Right > Hand Left
#   9   Reward > baseline

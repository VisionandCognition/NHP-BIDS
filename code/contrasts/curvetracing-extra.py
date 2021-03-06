# Curve tracing contrasts
contrasts = [
    ['AttendUL_COR>CurveNoResponse', 'T',  # t-test
     ['AttendUL_COR', 'CurveNoResponse'],
     [1.0, -1.0]],
    ['AttendDL_COR>CurveNoResponse', 'T',  # t-test
     ['AttendDL_COR', 'CurveNoResponse'],
     [1.0, -1.0]],
    ['AttendUR_COR>CurveNoResponse', 'T',  # t-test
     ['AttendUR_COR', 'CurveNoResponse'],
     [1.0, -1.0]],
    ['AttendDR_COR>CurveNoResponse', 'T',  # t-test
     ['AttendDR_COR', 'CurveNoResponse'],
     [1.0, -1.0]],
    ['Correct>Incorrect', 'T',  # t-test
     ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR',
      'CurveNotCOR'],
     [1.0, 1.0, 1.0, 1.0, -4.0]],
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


#   0   UL > No response
#   1   DL > No response
#   2   UR > No response
#   3   DR > No response
#   4   Correct > Incorrect (false, miss, break)
#   5   All Curves > Base
#   6   Attend Left > Attend Right
#   7   Attend Right > Attend Left
#   8   UL > other
#   9   DL > other
#  10   UR > other
#  11   DR > other
#  12   Hand Left > Hand Right
#  13   Hand Right > Hand Left
#  14   Reward > baseline

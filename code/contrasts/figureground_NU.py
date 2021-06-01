# Curve tracing contrasts
contrasts = [
    ['LeftFigure>Baseline', 'T',  # t-test
     ['Fig_LU', 'Fig_LN'], [1.0, 1.0]],
    ['RightFigure>Baseline', 'T',  # t-test
     ['Fig_RU', 'Fig_RN'], [1.0, 1.0]],
    ['RightFigure>LeftFigure', 'T',  # t-test
     ['Fig_LU', 'Fig_LN', 'Fig_RU', 'Fig_RN'], [-1.0, -1.0, 1.0, 1.0]],
    ['LeftFigure>RightFigure', 'T',  # t-test
     ['Fig_LU', 'Fig_LN', 'Fig_RU', 'Fig_RN'], [1.0, 1.0, -1.0, -1.0]],
    ['Fig_LU>Baseline', 'T',  # t-test
     ['Fig_LU'], [1.0]],
    ['Fig_LN>Baseline', 'T',  # t-test
     ['Fig_LN'], [1.0]],
    ['Fig_RU>Baseline', 'T',  # t-test
     ['Fig_RU'], [1.0]],
    ['Fig_RN>Baseline', 'T',  # t-test
     ['Fig_RN'], [1.0]],
    ['LeftFigure>Baseline', 'T',  # t-test
     ['Fig_LUB', 'Fig_LNB'], [1.0, 1.0]],
    ['RightFigure>Baseline', 'T',  # t-test
     ['Fig_RUB', 'Fig_RNB'], [1.0, 1.0]],
    ['RightFigure>LeftFigure', 'T',  # t-test
     ['Fig_LUB', 'Fig_LNB', 'Fig_RUB', 'Fig_RNB'], [-1.0, -1.0, 1.0, 1.0]],
    ['LeftFigure>RightFigure', 'T',  # t-test
     ['Fig_LUB', 'Fig_LNB', 'Fig_RUB', 'Fig_RNB'], [1.0, 1.0, -1.0, -1.0]],
    ['Fig_LUB>Baseline', 'T',  # t-test
     ['Fig_LUB'], [1.0]],
    ['Fig_LNB>Baseline', 'T',  # t-test
     ['Fig_LNB'], [1.0]],
    ['Fig_RUB>Baseline', 'T',  # t-test
     ['Fig_RUB'], [1.0]],
    ['Fig_RNB>Baseline', 'T',  # t-test
     ['Fig_RNB'], [1.0]],
    ['Reward>Baseline', 'T',  # t-test
     ['Reward'], [1.0]],
]

# STIM BASED =====
# 0 - LEFT > baseline
# 1 - RIGHT > baseline
# 2 - R > L
# 3 - L > R
# 4 - LU > baseline
# 5 - LN > baseline
# 6 - RU > baseline
# 7 - RN > baseline

# BLOCK BASED =====
# 8 - LEFT > baseline
# 9 - RIGHT > baseline
# 10 - RB > LB
# 11 - LB > RB
# 12 - LUB > baseline
# 13 - LNB > baseline
# 14 - RUB > baseline
# 15 - RNB > baseline

# REWARD ======
# 16 - Reward > baseline

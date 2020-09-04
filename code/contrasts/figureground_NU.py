# Curve tracing contrasts
contrasts = [
    ['LeftFigure>Baseline', 'T',  # t-test
     ['Fig_LUB', 'Fig_LNB'], [1.0, 1.0]],
    ['RightFigure>Baseline', 'T',  # t-test
     ['Fig_RUB', 'Fig_RNB'], [1.0, 1.0]],
    ['RightFigure>LeftFigure', 'T',  # t-test
     ['Fig_LUB', 'Fig_LNB', 'Fig_RUB', 'Fig_RNB'],
     [-1.0, -1.0, 1.0, 1.0]],
    ['LeftFigure>RightFigure', 'T',  # t-test
     ['Fig_LUB', 'Fig_LNB', 'Fig_RUB', 'Fig_RNB'],
     [1.0, 1.0, -1.0, -1.0]],
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
# 8 - Reward > baseline
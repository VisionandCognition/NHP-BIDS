# Curve tracing contrasts
contrasts = [
    ['LeftFigure>Baseline', 'T',  # t-test
     ['Fig_LUB', 'Fig_LDB'], [1.0, 1.0]],
    ['RightFigure>Baseline', 'T',  # t-test
     ['Fig_RUB', 'Fig_RDB'], [1.0, 1.0]],
    ['RightFigure>LeftFigure', 'T',  # t-test
     ['Fig_LUB', 'Fig_LDB', 'Fig_RUB', 'Fig_RDB'],
     [-1.0, -1.0, 1.0, 1.0]],
    ['LeftFigure>RightFigure', 'T',  # t-test
     ['Fig_LUB', 'Fig_LDB', 'Fig_RUB', 'Fig_RDB'],
     [1.0, 1.0, -1.0, -1.0]],
    ['Fig_LUB>Baseline', 'T',  # t-test
     ['Fig_LUB'], [1.0]],
    ['Fig_LDB>Baseline', 'T',  # t-test
     ['Fig_LDB'], [1.0]],
    ['Fig_RUB>Baseline', 'T',  # t-test
     ['Fig_RUB'], [1.0]],
    ['Fig_RDB>Baseline', 'T',  # t-test
     ['Fig_RDB'], [1.0]],
    ['Reward>Baseline', 'T',  # t-test
     ['Reward'], [1.0]],
]

# BLOCK BASED =====
# 0 - LEFT > baseline
# 1 - RIGHT > baseline
# 2 - R > L
# 3 - L > R
# 4 - LU > baseline
# 5 - LD > baseline
# 6 - RU > baseline
# 7 - RD > baseline
# 8 - Reward > baseline
# Curve tracing contrasts
contrasts = [
    ['LeftFigure>Baseline', 'T',  # t-test
     ['Fig_LU', 'Fig_LD'], [1, 1]],
    ['RightFigure>Baseline', 'T',  # t-test
     ['Fig_RU', 'Fig_RD'], [1, 1]],
    ['RightFigure>LeftFigure', 'T',  # t-test
     ['Fig_LU', 'Fig_LD', 'Fig_RU', 'Fig_RD'],
     [-1.0, -1.0, 1.0, 1.0]],
    ['LeftFigure>RightFigure', 'T',  # t-test
     ['Fig_LU', 'Fig_LD', 'Fig_RU', 'Fig_RD'],
     [1.0, 1.0, -1.0, -1.0]],
    ['Fig_LU>Baseline', 'T',  # t-test
     ['Fig_LU'], [1]],
    ['Fig_LD>Baseline', 'T',  # t-test
     ['Fig_LD'], [1]],
    ['Fig_RU>Baseline', 'T',  # t-test
     ['Fig_RU'], [1]],
    ['Fig_RD>Baseline', 'T',  # t-test
     ['Fig_RD'], [1]],
    ['Reward>Baseline', 'T',  # t-test
     ['Reward'], [1.0]],
]

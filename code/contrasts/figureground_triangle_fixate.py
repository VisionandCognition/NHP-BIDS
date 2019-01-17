# Curve tracing contrasts
contrasts = [
    ['LeftFigure>Baseline', 'T',  # t-test
     ['Triangle_LU', 'Triangle_LD'],
     [1,1],
    ['RightFigure>Baseline', 'T',  # t-test
     ['Triangle_RU', 'Triangle_RD'],
     [1,1],
    ['RightFigure>LeftFigure', 'T',  # t-test
     ['Triangle_LU', 'Triangle_LD', 'Triangle_RU', 'Triangle_RD'],
     [-1.0, -1.0, 1.0, 1.0]],
    ['LeftFigure>RightFigure', 'T',  # t-test
     ['Triangle_LU', 'Triangle_LD', 'Triangle_RU', 'Triangle_RD'],
     [1.0, 1.0, -1.0, -1.0]],

    ['Triangle_LU>R', 'T',  # t-test
     ['Triangle_LU','Triangle_LD', 'Triangle_RU', 'Triangle_RD'],
     [3,-1,-1,-1],
    ['Triangle_LD>R', 'T',  # t-test
     ['Triangle_LU','Triangle_LD', 'Triangle_RU', 'Triangle_RD'],
     [-1,3,-1,-1],
    ['Triangle_RU>R', 'T',  # t-test
     ['Triangle_LU','Triangle_LD', 'Triangle_RU', 'Triangle_RD'],
     [-1,-1,3,-1],
    ['Triangle_RD>R', 'T',  # t-test
     ['Triangle_LU','Triangle_LD', 'Triangle_RU', 'Triangle_RD'],
     [-1,-1,-1,3],
    
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

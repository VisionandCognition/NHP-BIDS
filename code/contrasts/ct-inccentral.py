# Curve tracing contrasts inc. 'vsCentralTask'
contrasts = [
	['Curves>Baseline', 'T', 
	 ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR', 'AttendCenter_COR'], 
	 [0.2, 0.2, 0.2, 0.2, 0.2]], 
	['AttendLeft>AttendRight', 'T', 
	 ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR'], 
	 [1.0, 1.0, -1.0, -1.0]], 
	['AttendRight>AttendLeft', 'T', 
	 ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR'], 
	 [-1.0, -1.0, 1.0, 1.0]], 
	['AttendUL>AttendOther', 'T', 
	 ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR'], 
	 [3.0, -1.0, -1.0, -1.0]], 
	['AttendDL>AttendOther', 'T', 
	 ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR'], 
	 [-1.0, 3.0, -1.0, -1.0]], 
	['AttendUR>AttendOther', 'T', 
	 ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR'], 
	 [-1.0, -1.0, 3.0, -1.0]], 
	['AttendDR>AttendOther', 'T', 
	 ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR'], 
	 [-1.0, -1.0, -1.0, 3.0]], 
	['HandLeft>HandRight', 'T', 
	 ['HandLeft', 'HandRight'], 
	 [1.0, -1.0]], 
	['HandRight>HandLeft', 'T', 
	 ['HandLeft', 'HandRight'], 
	 [-1.0, 1.0]], 
	['Reward>Baseline', 'T', 
	 ['Reward'], 
	 [1.0]], 
	['AttendCurves>AttendCenter', 'T', 
	 ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR', 'AttendCenter_COR'], 
	 [1.0, 1.0, 1.0, 1.0, -4.0]], 
	['AttendUL>AttendCenter', 'T', 
	 ['AttendUL_COR', 'AttendCenter_COR'], 
	 [1.0, -1.0]], 
	['AttendDL>AttendCenter', 'T', 
	 ['AttendDL_COR', 'AttendCenter_COR'], 
	 [1.0, -1.0]], 
	['AttendUR>AttendCenter', 'T', 
	 ['AttendUR_COR', 'AttendCenter_COR'], 
	 [1.0, -1.0]], 
	['AttendDR>AttendCenter', 'T', 
	 ['AttendDR_COR', 'AttendCenter_COR'], 
	 [1.0, -1.0]], 
	['Correct>Incorrect', 'T', 
	 ['AttendUL_COR', 'AttendDL_COR', 'AttendUR_COR', 'AttendDR_COR', 'CurveNotCOR'], 
	 [1.0, 1.0, 1.0, 1.0, -4.0]]
]

'''
0   All Curves > Base
1   Attend Left > Attend Right
2   Attend Right > Attend Left
3   UL > other
4   DL > other
5   UR > other
6   DR > other
7   Hand Left > Hand Right
8   Hand Right > Hand Left
9   Reward > baseline
10	All Curves > Center
11  UL > Central
12  DL > Central
13  UR > Central
14  DR > Central
15  Correct > Incorrect
'''

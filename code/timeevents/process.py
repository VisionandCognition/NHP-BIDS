def process_events(event_log, TR, in_nvols):
    import re
    tmat = re.search(r'task-([^_-]+)', event_log)
    if tmat is None:
        raise RuntimeError('Could not parse task from %s! '
                'Required for processing time events.' % event_log)

    if tmat.group(1) == 'ctcheckerboard':  # task from filename
        print('Using ctcheckerboard to calculate regressors')
        from timeevents.ctcheckerboard import process_events as process_events_for_task
    elif tmat.group(1) == 'curvetracing' or tmat.group(1) == 'curvetracinginccentral':
        print('Using curvetracing to calculate regressors')
        from timeevents.curvetracing import process_events as process_events_for_task
    elif tmat.group(1) == 'figureground' or tmat.group(1) == 'figgnd':
        # print('Using figureground to calculate regressors')
        # from timeevents.figureground import process_events as process_events_for_task 
        print('Using figureground_NU to calculate regressors')
        from timeevents.figureground_NU import process_events as process_events_for_task        
    elif tmat.group(1) == 'figureground_localizer' or tmat.group(1) == 'figgndloc':
        #print('Using figureground to calculate regressors')
        #from timeevents.figureground import process_events as process_events_for_task  
        print('Using figureground_NU to calculate regressors')
        from timeevents.figureground_NU import process_events as process_events_for_task     
    else:
        raise RuntimeError('Unknown experimental task %s. '
                'Needed for ' % tmat.group(1))

    return process_events_for_task(event_log, TR, in_nvols)

import nipype.interfaces.utility as niu


process_time_events = niu.Function(
    input_names=['event_log', 'TR', 'in_nvols'],
    output_names=['out_events', 'out_end_time_s', 'out_nvols'],
    function=process_events,
)

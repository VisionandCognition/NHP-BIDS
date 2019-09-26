#!/usr/bin/env python3
import nipype.interfaces.utility as niu

def process_events(event_log, TR, in_nvols):
    # necessary for importing with NiPype
    import pandas as pd

    class Event(object):
        def __init__(self, start_s, stop_s=None, event_num=1,
                     dur_s=None, amplitude=1):
            self.time_s = start_s
            if dur_s is not None:
                self.dur_s = float(dur_s)
            elif stop_s is not None:
                self.dur_s = stop_s - start_s
            else:
                self.dur_s = 0

            self.event_num = event_num
            self.amplitude = amplitude

    events = pd.read_csv(event_log, na_values='n/a', sep='\t', header=0)

    split_ev = {
        'Fig_LU': [],  # Left upwards pointing triangle
        'Fig_LD': [],  # Left downwards pointing triangle
        'Fig_RU': [],  # Right upwards pointing triangle
        'Fig_RD': [],  # Right downwards pointing triangle
        'Fig_LUB': [],  # Left upwards pointing triangle block
        'Fig_LDB': [],  # Left downwards pointing triangle block
        'Fig_RUB': [],  # Right upwards pointing triangle block
        'Fig_RDB': [],  # Right downwards pointing triangle block
        'Reward': [],
        'Fixating': [],
    }
    last_block_end = -15

    StimType = None
    FigShape = None
    FigSide = None
    FigOn = False
    GndOn = False
    FigBlockStarted = False
    GndBlockStarted = False

    mri_triggers = events[(events['event'] == 'MRI_Trigger') &
                          (events['info'] == 'Received')]
    start_time_s = mri_triggers.iloc[0].time_s
    events['time_s'] = events['time_s'] - start_time_s

    for irow, event in events.iterrows():
        if irow > mri_triggers.index[0]:
            if event.task == 'FigGnd':
                if event.event == 'StimType':
                    StimType = event.info
                if FigOn is False and GndOn is False:
                    if event.event == 'FigShape':
                        FigShape = event.info
                    elif event.event == 'FigLoc':
                        FigSide = event.info
                    elif event.event == 'FigOrient':
                        FigOrient = event.info
                    elif event.event == 'Figure' and event.info == 'start':
                        fig_start_time = event.time_s
                        FigOn = True
                        GndOn = False
                        if FigBlockStarted is False:
                            figblock_start_time = fig_start_time
                            FigBlockStarted = True
                            GndBlockStarted = False
                    elif event.event == 'Ground' and event.info == 'start':
                        gnd_start_time = event.time_s
                        GndOn = True
                        FigOn = False
                        if GndBlockStarted is False:
                            gndblock_start_time = gnd_start_time
                            GndBlockStarted = True
                        if FigBlockStarted is True:
                            figblock_dur = event.time_s - figblock_start_time
                            if FigShape == 'Triangle_up' and FigSide == 'left':
                                split_ev['Fig_LUB'].append(Event(
                                    figblock_start_time, dur_s=figblock_dur))
                            elif FigShape == 'Triangle_down' and FigSide == 'left':
                                split_ev['Fig_LDB'].append(Event(
                                    figblock_start_time, dur_s=figblock_dur))
                            elif FigShape == 'Triangle_up' and FigSide == 'right':
                                split_ev['Fig_RUB'].append(Event(
                                    figblock_start_time, dur_s=figblock_dur))
                            elif FigShape == 'Triangle_down' and FigSide == 'right':
                                split_ev['Fig_RDB'].append(Event(
                                    figblock_start_time, dur_s=figblock_dur))
                            FigBlockStarted = False
                elif FigOn is True and GndOn is False:
                    if event.event == 'Figure' and event.info == 'stop':
                        fig_stop_time = event.time_s  # getting overwritten
                        last_block_end = fig_stop_time
                        FigOn = False
                        fig_dur = fig_stop_time - fig_start_time
                        if FigShape == 'Triangle_up' and FigSide == 'left':
                            split_ev['Fig_LU'].append(Event(
                                fig_start_time, dur_s=fig_dur))
                        elif FigShape == 'Triangle_down' and FigSide == 'left':
                            split_ev['Fig_LD'].append(Event(
                                fig_start_time, dur_s=fig_dur))
                        elif FigShape == 'Triangle_up' and FigSide == 'right':
                            split_ev['Fig_RU'].append(Event(
                                fig_start_time, dur_s=fig_dur))
                        elif FigShape == 'Triangle_down' and FigSide == 'right':
                            split_ev['Fig_RD'].append(Event(
                                fig_start_time, dur_s=fig_dur))
                elif FigOn is False and GndOn is True:
                    if event.event == 'Ground' and event.info == 'stop':
                        gnd_stop_time = event.time_s
                        last_block_end = gnd_stop_time
                        GndOn = False
                    elif event.event == 'Figure' and event.info == 'start':
                        fig_start_time = event.time_s
                        FigOn = True
                        GndOn = False
            elif event.task == 'Fixate':
                if event.info == 'start':
                    fix_start_time = event.time_s
                elif event.info == 'stop':
                    fix_stop_time = event.time_s
                    fix_dur = fix_stop_time - fix_start_time
                    split_ev['Fixating'].append(Event(
                                fix_start_time, dur_s=fix_dur))
            elif event.task == 'Reward':
                if event.info == 'start':
                    rew_start_time = event.time_s
                elif event.info == 'stop':
                    rew_stop_time = event.time_s
                    rew_dur = rew_stop_time - rew_start_time
                    split_ev['Reward'].append(Event(
                                rew_start_time, dur_s=rew_dur,
                                amplitude=rew_dur))
    end_time_s = min(
        last_block_end + 15,
        events.iloc[len(events) - 1]['time_s'])

    nvols = min(
        int(end_time_s / TR),
        in_nvols)

    cond_events = dict()
    for key, events in split_ev.items():
        cevents = []
        for ev in events:
            cevents.append({
                'time': ev.time_s,
                'dur': ev.dur_s,
                'amplitude': ev.amplitude})
        cond_events[key] = pd.DataFrame(cevents, dtype=float)

    return (cond_events, end_time_s, nvols)


calc_figgnd_events = niu.Function(
    input_names=['event_log', 'TR', 'in_nvols'],
    output_names=['out_events', 'out_end_time_s', 'out_nvols'],
    function=process_events,
)

if __name__ == '__main__':
    calc_figgnd_events.inputs.event_log = (
        'sub-danny_ses-20190517_task-figureground_run-06_events.tsv')
    calc_figgnd_events.inputs.TR = 2.5
    calc_figgnd_events.inputs.in_nvols = 280
    res = calc_figgnd_events.run()

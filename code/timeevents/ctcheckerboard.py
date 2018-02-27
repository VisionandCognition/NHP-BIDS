#!/usr/bin/env python3


def process_events(event_log, TR, in_nvols):
    # necessary for importing with NiPype
    import pandas as pd

    class Event(object):
        def __init__(self, start_s, stop_s=None, event_num=1, dur_s=None, amplitude=1):
            self.time_s = start_s
            if dur_s is not None:
                self.dur_s = float(dur_s)
            elif stop_s is not None:
                self.dur_s = stop_s - start_s
            else:
                self.dur_s = 0

            self.event_num = event_num
            self.amplitude = amplitude

    events = pd.read_table(event_log, na_values='n/a')

    split_ev = {
        'GapL': [],
        'GapR': [],
        'GapDL': [],
        'GapDR': [],
        'GapUL': [],
        'GapUR': [],
        'CurveSegL': [],
        'CurveSegR': [],
        'CurveSegDL': [],
        'CurveSegDR': [],
        'CurveSegUL': [],
        'CurveSegUR': [],
        'CircleDL': [],
        'CircleDR': [],
        'CircleUL': [],
        'CircleUR': [],

        # Not a hand task! Need to revisit...
        'CurveFalseHit': [],  # False hit / wrong hand
        'CurveFixationBreak': [],

        'PreSwitchCurves': [],  # All PreSwitch displays with Curves & targets
        'ResponseCues': [],  # All response cues events, unless
                             # subject is not fixating at all
        'Reward': [],
        'FixationTask': [],
        'Fixating': [],
    }
    last_correct_s = -15

    curve_stim = None
    curve_stim_on = None
    curve_response = None
    curve_switched = False

    fixation_stim_on = None
    response_cues_on = None
    curr_state = None
    began_fixation = None
    has_ManualRewardField = False

    mri_triggers = events[(events['event'] == 'MRI_Trigger') &
                          (events['info'] == 'Received')]
    start_time_s = mri_triggers.iloc[0].time_s

    events['time_s'] = events['time_s'] - start_time_s
    events['record_time_s'] = events['record_time_s'] - start_time_s

    for irow, event in events.iterrows():
        if event.event == 'NewState':
            curr_state = event.info
            if curr_state == 'SWITCHED':
                curve_switched = True

        if event.event == 'Fixation':
            if event.info == 'Out':
                if began_fixation is not None:
                    split_ev['Fixating'].append(
                        Event(began_fixation, event.time_s))
                began_fixation = None
            else:
                assert event.info == 'In', (
                    'Unrecognized fixation event info "%s"' % event.info)
                began_fixation = event.time_s

        if event.event == 'CombinedStim':
            curve_stim = set(
                    event.info.split('+')
                    ).difference({'BlankL', 'BlankR'})

        elif event.event == 'NewState' and event.info == 'TRIAL_END':
            curve_stim = None
            curve_stim_on = None
            curve_response = None
            curve_switched = False

            fixation_stim_on = None
            response_cues_on = None

        elif (event.task == 'Fixation' and event.event == 'NewState' and
              event.info == 'FIXATION_PERIOD'):
            fixation_stim_on = event.time_s

        elif event.event == 'NewState' and event.info == 'FIXATION_PERIOD':
            assert curve_stim is not None
            curve_stim_on = event.time_s

        elif (event.task == 'Fixation' and event.event == 'NewState' and
              event.info == 'POSTFIXATION'):
            split_ev['FixationTask'].append(
                Event(fixation_stim_on, event.time_s))

        elif event.event == 'NewState' and event.info == 'SWITCHED':
            response_cues_on = event.time_s

        elif (event.event == 'NewState' and
                event.info == 'POSTFIXATION' and
                event.task != 'Fixation'):

            assert (event.task == 'CT-Shaped Checkerboard RH' or
                    event.task == 'CT-Shaped Checkerboard LH')

            assert curve_stim_on is not None

            split_ev['PreSwitchCurves'].append(
                Event(curve_stim_on, event.time_s))

            event_type = curve_stim
            if curve_response == 'INCORRECT':  # shouldn't happen with fix task
                assert False
                event_type = {'CurveFalseHit'}

            elif curve_response is None:
                assert False
                if not curve_switched:
                    event_type = {'CurveFixationBreak'}

            elif curve_response == 'FixationBreak':
                event_type = {'CurveFixationBreak'}

            else:
                last_correct_s = event.time_s
                assert curve_response == 'CORRECT', (
                    'Unhandled curve_response %s' % curve_response)

            for evt in event_type:
                split_ev[evt].append(Event(curve_stim_on, event.time_s))

            if response_cues_on is not None:
                # regardless of whether it is correct or not
                # TODO: should not add if eyes are closed
                split_ev['ResponseCues'].append(Event(response_cues_on,
                                                      event.time_s))

        elif event.event == 'ResponseGiven' and curve_response is None:
            curve_response = event.info

        # elif event.event == 'Fixation' and event.info == 'Out'
        #  and curve_response is None:
        #    curve_response = 'FixationBreak'

        # elif event.event == 'Response_Initiate':
        #     split_ev['Hand%s' % event.info].append(Event(event.time_s))

        elif event.event == 'ResponseReward' or event.event == 'TaskReward':
            reward_dur = event.info
            split_ev['Reward'].append(Event(event.time_s, amplitude=reward_dur))

        elif event.event == 'ManualReward':
            reward_dur = event.info
            has_ManualRewardField = True
            split_ev['Reward'].append(Event(event.time_s, amplitude=reward_dur))

        elif event.event == 'Reward' and event.info == 'Manual':
            split_ev['Reward'].append(Event(event.time_s, amplitude=0.04))
            assert not has_ManualRewardField, (
                "Event log should not have ('Reward','Manual') "
                "entry if it has ('ManualReward') entry.")

    end_time_s = min(
        last_correct_s + 15,
        events.iloc[len(events) - 1]['time_s'])
    # end_time_s = events.iloc[len(events) - 1]['time_s']

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

    print("\n\n\nFinished processing: %s" % event_log)
    return (cond_events, end_time_s, nvols)


import nipype.interfaces.utility as niu


calc_curvetracing_events = niu.Function(
    input_names=['event_log', 'TR', 'in_nvols'],
    output_names=['out_events', 'out_end_time_s', 'out_nvols'],
    function=process_events,
)

if __name__ == '__main__':
    calc_curvetracing_events.inputs.event_log = (
        '/big/NHP_MRI/BIDS_raw/sub-eddy/ses-20170614/func/'
        'sub-eddy_ses-20170614_task-curvetracing_run-02_events.tsv')
    calc_curvetracing_events.inputs.TR = 2.5
    calc_curvetracing_events.inputs.in_nvols = 420
    res = calc_curvetracing_events.run()

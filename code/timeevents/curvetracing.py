#!/usr/bin/env python3
import os
import sys
import glob
import re
import pandas as pd

import pdb
import errno

import subprocess


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class Event(object):
    def __init__(self, start_s, stop_s=None, event_num=1, dur_s=None):
        self.time_s = start_s
        if dur_s is not None:
            self.dur_s = float(dur_s)
        elif stop_s is not None:
            self.dur_s = stop_s - start_s
        else:
            self.dur_s = 0

        self.event_num = event_num


def process_events(event_log, TR, nvols):
    events = pd.read_tsv(event_log)

    split_ev = {
        'CurveUL': [],  # When correct response
        'CurveDL': [],
        'CurveUR': [],
        'CurveDR': [],
        'CurveCenter': [],
        'CurveIncorrect': [],  # False hit / wrong hand
        'CurveNoResponse': [],
        'CurveFixationBreak': [],
        'CurveNotCorrect': [],  # Catch-all: Incorrect, NoResponse, Fix. Break

        'PreSwitchCurves': [],  # All PreSwitch displays with Curves & targets
        'ResponseCues': [],  # All response cues events, unless
                             # subject is not fixating at all
        'HandLeft': [],
        'HandRight': [],
        'Reward': [],
        'FixationTask': [],
        'Fixating': [],
    }
    last_correct_s = -15

    curve_target = None
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

        if event.event == 'TargetLoc':
            curve_target = event.info

        elif event.event == 'NewState' and event.info == 'TRIAL_END':
            curve_target = None
            curve_stim_on = None
            curve_response = None
            curve_switched = False

            fixation_stim_on = None
            response_cues_on = None

        elif event.event == 'NewState' and event.info == 'PRESWITCH':
            assert curve_target is not None
            curve_stim_on = event.time_s

        elif (event.task == 'Fixation' and event.event == 'NewState' and
              event.info == 'FIXATION_PERIOD'):
            fixation_stim_on = event.time_s

        elif (event.task == 'Fixation' and event.event == 'NewState' and
              event.info == 'POSTFIXATION'):
            split_ev['FixationTask'].append(
                Event(fixation_stim_on, event.time_s))

        elif event.event == 'NewState' and event.info == 'SWITCHED':
            response_cues_on = event.time_s

        elif event.event == 'NewState' and (
            event.info == 'POSTSWITCH') and (
                event.task != 'Fixation'):

            assert (event.task == 'Curve tracing' or
                    event.task == 'Control CT' or
                    event.task == 'Catch CT' or
                    event.task == 'Keep busy')

            assert curve_stim_on is not None

            split_ev['PreSwitchCurves'].append(
                Event(curve_stim_on, event.time_s))

            event_type = 'Curve%s' % curve_target
            if curve_response == 'INCORRECT':
                event_type = 'CurveIncorrect'

            elif curve_response is None:
                if curve_switched:
                    event_type = 'CurveNoResponse'
                else:
                    event_type = 'CurveFixationBreak'

            elif curve_response == 'FixationBreak':
                event_type = 'CurveFixationBreak'

            else:
                last_correct_s = event.time_s
                assert curve_response == 'CORRECT', (
                    'Unhandled curve_response %s' % curve_response)

            split_ev[event_type].append(Event(curve_stim_on, event.time_s))
            if (event_type == 'CurveIncorrect' or
                    event_type == 'CurveNoResponse' or
                    event_type == 'CurveFixationBreak'):
                split_ev['CurveNotCorrect'].append(
                    Event(curve_stim_on, event.time_s))

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

        elif event.event == 'Response_Initiate':
            split_ev['Hand%s' % event.info].append(Event(event.time_s))

        elif event.event == 'ResponseReward' or event.event == 'TaskReward':
            reward_dur = event.info
            split_ev['Reward'].append(Event(event.time_s, dur_s=reward_dur))

        elif event.event == 'ManualReward':
            reward_dur = event.info
            has_ManualRewardField = True
            split_ev['Reward'].append(Event(event.time_s, dur_s=reward_dur))

        elif event.event == 'Reward' and event.info == 'Manual':
            split_ev['Reward'].append(Event(event.time_s, dur_s=0.04))
            assert not has_ManualRewardField, (
                "Event log should not have ('Reward','Manual') "
                "entry if it has ('ManualReward') entry.")

    end_time_s = min(
        last_correct_s + 15,
        events.iloc[len(events) - 1]['time_s'])
    # end_time_s = events.iloc[len(events) - 1]['time_s']

    nvols = min(
        int(end_time_s / TR),
        nvols)

    return (split_ev, end_time_s)


def main(session_path, beh_paths=None):
    if beh_paths is None:
        beh_paths = glob.glob('%s/run0[0-9][0-9]/behavior' % (session_path))
        beh_paths.sort()

    for cur_beh in beh_paths:
        try:
            run_path = os.path.dirname(os.path.abspath(cur_beh))
            run = os.path.split(run_path)[1]
            assert len(run), ("Could not process behavior directory %s" %
                              cur_beh)

            beh_dir = os.path.join(session_path, run, 'behavior')
            if not os.path.isdir(cur_beh):
                print('Path not found for %s: %s' % (run, cur_beh))
                continue

            print('---------------------------------')
            print('\nProcessing behavior of %s.' % run)

            split_events = None
            task_dirs = glob.glob('%s/*/' % (beh_dir))
            assert len(task_dirs), 'The behavior directory %s should have at' \
                ' least one subdirectory'

            task_group_paths = glob.glob('%s/*/' % (beh_dir))
            assert len(task_group_paths) == 1
            task_group_path = task_group_paths[0]

            print(task_group_path)

            # Find the overall/event log file
            eventlog_pat = re.compile(r'Log_.*_\d+T\d+(?:_eventlog)?\.csv')
            csv_logs = [os.path.split(f)[1] for f in glob.glob(
                '%s/Log_*.csv' % task_group_path)]
            matches = [re.match(eventlog_pat, log) is
                       not None for log in csv_logs]

            event_log = [log for log, match in
                         zip(csv_logs, matches) if match]
            assert len(event_log) != 0, (
                "There were no matching event logs in %s" % task_group_path)
            assert len(event_log) <= 1, (
                "There must only be one event log in %s." % task_group_path)

            events = pd.read_csv(os.path.join(
                task_group_path,
                event_log[0]))

            assert split_events is None, (
                'Events need to be merged before '
                'multiple task groups are handled.')

            (split_events, end_time_s) = process_events(events)

            print(' '.join(cmd))
            subprocess.call(cmd)

            mkdir_p(os.path.join(run_path, 'model'))

            for task, task_events in split_events.items():
                # open file in model directory
                model_path = os.path.join(run_path, 'model', '%s.txt' % task)

                with open(model_path, 'w') as f:
                    for ev in task_events:
                        f.write('%03f\t%f\t%d\n' %
                                (ev.time_s, ev.dur_s, ev.event_num))
        except Exception as e:
            print("\n\nError processing %s:" % cur_beh)
            print(str(e))
            print("\n\n")

    print('You may now want to run:')
    print('\tpmri_get_motion_outliers . fois_roi.nii.gz')


if __name__ == '__main__':
    session_path = None
    beh_paths = None
    if len(sys.argv) <= 2 and len(glob.glob('run???')):
        session_path = os.getcwd()
    else:
        print("No 'run0xx' directory found in current location.")

    if len(sys.argv) == 2:
        if session_path is None:
            session_path = sys.argv[1]
        else:
            beh_paths = [sys.argv[1]]
    elif len(sys.argv) == 3:
        session_path = sys.argv[1]
        beh_paths = [sys.argv[2]]

    if session_path is not None:
        sys.exit(main(session_path, beh_paths))
    else:
        print("Syntax:")
        print("\t%s [session_path] [behavior_paths]")
        print("\nWhere session_path is a directory that contains "
              "run0xx directories.")
        print("session_path is optional if the current directory "
              "contains run0xx directories")
        print("behavior_paths by default is all the run0xx directories.")

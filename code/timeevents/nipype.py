import nipype.interfaces.utility as niu

from .curvetracing import process_events

calc_curvetracing_events = niu.Function(
    input_names=['in_file', 'TR', 'in_nvols'],
    output_names=['out_events', 'out_end_time_s', 'out_nvols'],
    function=process_events)

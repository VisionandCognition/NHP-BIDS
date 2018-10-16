def run_workflow(session, csv_file, use_pbs, stop_on_first_crash,
                 ignore_events, types):
    import bids_templates as bt

    from nipype import config
    config.enable_debug_mode()

    # ------------------ Specify variables
    ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    data_dir = ds_root
    output_dir = ''
    working_dir = 'workingdirs/minimal_processing'

    # ------------------ Input Files
    # Get info from csv
    reader = niu.CSVReader()
    reader.inputs.header = True
    reader.inputs.in_file = csv_file
    out = reader.run()
    subject_list = out.outputs.subject
    session_list = out.outputs.session
    type_list = out.outputs.type
    run_list = out.outputs.run
    ev_list = out.outputs.ev

    # initiate separate lists
    hires.sub = []
    hires.ses = []
    anat.list = []
    func.list = []
    func_ev_list = []

    listind = 0  # keep track of list content
    for entry in type_list:
        if entry == 'func':  # 1 mm iso and check events
            if ev_list[listind] == 1:
                # add to do_ev_list
                list.append(func_ev_list,)

        elif entry == 'anat':  # 1 and 0.6 mm iso
        else:
            # 1mm iso
        listind = listind + 1
            








    infosource = Node(IdentityInterface(fields=[
        'subject_id',
        'session_id',
    ]), name="infosource")

    reader = niu.CSVReader()
    reader.inputs.header = True
    reader.inputs.in_file = csv_file
    out = reader.run()
    subject_list = out.outputs.subject
    session_list = out.outputs.session
    infosource.iterables = [
        ('session_id', session_list),
        ('subject_id', subject_list),
    ]
    if 'run' in out.outputs.traits().keys():
        print('Ignoring the "run" field of %s.' % csv_file)

    infosource.synchronize = True

    process_images = True









    if process_images:
        datatype_list = types.split(',')

        imgsource = Node(IdentityInterface(fields=[
            'subject_id', 'session_id', 'datatype',
        ]), name="imgsource")
        imgsource.iterables = [
            ('session_id', session_list), ('subject_id', subject_list),
            ('datatype', datatype_list),
        ]

        # SelectFiles
        # HERE FILES ARE SELECTED FOR INPUT IN WORKFLOWS !!
        imgfiles = Node(
            nio.SelectFiles({
                'images':
                'sourcedata/%s' % bt.templates['images'],
            }, base_directory=data_dir), name="img_files")





















    if not ignore_events:  # only create an event node when handling events
        evsource = Node(IdentityInterface(fields=[
            'subject_id', 'session_id',
        ]), name="evsource")
        evsource.iterables = [
            ('session_id', session_list), ('subject_id', subject_list),
        ]
        evfiles = Node(
            nio.SelectFiles({
                'csv_eventlogs':
                'sourcedata/sub-{subject_id}/ses-{session_id}/func/'
                'sub-{subject_id}_ses-{session_id}_*events/Log_*_eventlog.csv',
                'stim_dir':
                'sourcedata/sub-{subject_id}/ses-{session_id}/func/'
                'sub-{subject_id}_ses-{session_id}_*events/',
            }, base_directory=data_dir), name="evfiles")

    







    # ------------------ Output Files
    # Datasink
    outputfiles = Node(nio.DataSink(
        base_directory=ds_root,
        container=output_dir,
        parameterization=True),
        name="output_files")

    # Use the following DataSink output substitutions
    outputfiles.inputs.substitutions = [
        ('subject_id_', 'sub-'),
        ('session_id_', 'ses-'),
        ('/minimal_processing/', '/'),
        ('_out_reoriented.nii.gz', '.nii.gz')
    ]
    # Put result into a BIDS-like format
    outputfiles.inputs.regexp_substitutions = [
        (r'_datatype_([a-z]*)_ses-([a-zA-Z0-9]*)_sub-([a-zA-Z0-9]*)',
            r'sub-\3/ses-\2/\1'),
        (r'/_ses-([a-zA-Z0-9]*)_sub-([a-zA-Z0-9]*)',
            r'/sub-\2/ses-\1/'),
        (r'/_ro[0-9]+/', r'/'),
        (r'/_csv2tsv[0-9]+/', r'/func/'),
    ]

    





















    # -------------------------------------------- Create Pipeline
    workflow = Workflow(
        name='wrapper',
        base_dir=os.path.join(ds_root, working_dir))

    if process_images:
        workflow.connect([(imgsource, imgfiles,
                           [('subject_id', 'subject_id'),
                            ('session_id', 'session_id'),
                            ('datatype', 'datatype'),
                            ])])
    if not ignore_events:
        workflow.connect([(evsource, evfiles,
                           [('subject_id', 'subject_id'),
                            ('session_id', 'session_id'),
                            ]),
                          ])

    if process_images:
        minproc = create_images_workflow()
        workflow.connect(imgfiles, 'images',
                         minproc, 'in.images')
        workflow.connect(minproc, 'out.images',
                         outputfiles, 'minimal_processing.@images')

    if not ignore_events:
        csv2tsv = MapNode(
            ConvertCSVEventLog(),
            iterfield=['in_file', 'stim_dir'],
            name='csv2tsv')
        workflow.connect(evfiles, 'csv_eventlogs',
                         csv2tsv, 'in_file')
        workflow.connect(evfiles, 'stim_dir',
                         csv2tsv, 'stim_dir')
        workflow.connect(csv2tsv, 'out_file',
                         outputfiles, 'minimal_processing.@eventlogs')

    workflow.stop_on_first_crash = stop_on_first_crash
    workflow.keep_inputs = True
    workflow.remove_unnecessary_outputs = False
    workflow.write_graph()
    # workflow.run(plugin='MultiProc', plugin_args={'n_procs' : 10})
    workflow.run()























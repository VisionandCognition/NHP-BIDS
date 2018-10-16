def create_images_workflow_anat():  # all anatomical files (anat/dwi/fmap)
    """ Correct for the sphinx position and use reorient to standard.
    """
    # This workflow takes input images and performs minimal processing
    # - correction for sphinx position
    # - reorientation to fsl standard
    # - resampling to isotropic voxels
    # ====== WORK IN PROGRESS ========
    # It should be cloned and adjusted to handle different file-types
    # ================================
    workflow = Workflow(
        name='minimal_proc')

    inputs = Node(IdentityInterface(fields=[
        'images',
    ]), name="in")
    outputs = Node(IdentityInterface(fields=[
        'images',
    ]), name="out")

    sphinx = MapNode(
        fs.MRIConvert(
            sphinx=True,
        ),
        iterfield=['in_file'],
        name='sphinx')

    workflow.connect(inputs, 'images',
                     sphinx, 'in_file')

    ro = MapNode(
        fsl.Reorient2Std(),
        iterfield=['in_file'],
        name='ro')

    rs_iso = MapNode(
        fs.MRIConvert(
            vs='1 1 1',
        ),
        iterfield=['in_file'],
        name='rs_iso')

    workflow.connect(sphinx, 'out_file',
                     ro, 'in_file')
    workflow.connect(ro, 'out_file',
                     rs_iso, 'in_file')
    workflow.connect(rs_iso, 'out_file',
                     outputs, 'images')

    return workflow


def create_images_workflow_hires():  # high-res anatomical files
    """ Correct for the sphinx position and use reorient to standard.
    """
    # This workflow takes input images and performs minimal processing
    # - correction for sphinx position
    # - reorientation to fsl standard
    # - resampling to isotropic voxels
    # ====== WORK IN PROGRESS ========
    # It should be cloned and adjusted to handle different file-types
    # ================================
    workflow = Workflow(
        name='minimal_proc')

    inputs = Node(IdentityInterface(fields=[
        'images',
    ]), name="in")
    outputs = Node(IdentityInterface(fields=[
        'images',
    ]), name="out")

    sphinx = MapNode(
        fs.MRIConvert(
            sphinx=True,
        ),
        iterfield=['in_file'],
        name='sphinx')

    workflow.connect(inputs, 'images',
                     sphinx, 'in_file')

    ro = MapNode(
        fsl.Reorient2Std(),
        iterfield=['in_file'],
        name='ro')

    rs_iso = MapNode(
        fs.MRIConvert(
            vs='0.6 0.6 0.6',
        ),
        iterfield=['in_file'],
        name='rs_iso')

    workflow.connect(sphinx, 'out_file',
                     ro, 'in_file')
    workflow.connect(ro, 'out_file',
                     rs_iso, 'in_file')
    workflow.connect(rs_iso, 'out_file',
                     outputs, 'images')

    return workflow
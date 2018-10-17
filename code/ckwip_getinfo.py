# Get image lists =====================================================
def get_info(csv_file):
    # Get info from csv
    reader = niu.CSVReader()
    reader.inputs.header = True
    reader.inputs.in_file = csv_file
    out = reader.run()
    csv = out.outputs  # assign the columns of the csv-file to 'csv'

    # create empty lists where we will put out to-be-processed files
    file_in.func = []
    file_in.anat = []
    file_in.hires = []
    file_in.ev = []

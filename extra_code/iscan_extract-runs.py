def main():
    import pandas as pd
    
    # Access the input arguments
    print(f"In-file: {infile}")
    print(f"Out-folder: {outfld}")

    # Process the iscan file
    iscan_file = infile
    iscan_parts = iscan_file.strip().split("/")
    eyefile = iscan_parts[-1].rsplit('.',1)[0]

    # get the runs
    GetRuns = False
    run = -1
    runs={}

    with open(iscan_file, "r", encoding="utf-8") as file:
        all_lines = file.readlines()
    
    nlines = len(all_lines)
    line_cnt = 0;
    # go through lines
    with open(iscan_file, "r", encoding="utf-8") as file:   
        for line in file:
            line_cnt = line_cnt+1
            data = line.strip().split("\t")  # Split each line by tab
                    
            if data[0] == 'DATA INFO':
                GetRuns = True
                AddData = False
            
            if GetRuns:
                if len(data)>1:
                    if data[1] == 'Pupil H1 ':
                        Hdr = data
                        run = run+1 
                        datacollect = [Hdr]
                        AddData = True
    
                    elif AddData & (data[0] != 'Sample #'):
                        datacollect.append(data)
                        
                elif AddData:
                    AddData = False
                    runs[run] = pd.DataFrame(datacollect[1:], columns=datacollect[0])
    
                if line_cnt == nlines:
                    AddData = False
                    runs[run] = pd.DataFrame(datacollect[1:], columns=datacollect[0])
    # save as csv files
    for r in runs:
        runs[r].to_csv(eyefile + '_eye-run-' + str(r+1) + '.csv', index=False)

if __name__ == "__main__":
    import argparse
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="A script that extracts")
    # Define expected arguments
    parser.add_argument("--in", dest='infile', type=str, required=True, help="The full path of the iscan file")
    parser.add_argument("--out", dest='outfld', type=str, required=True, help="The full output path of the extracted iscan runs")
    # Parse the arguments
    args = parser.parse_args()
    main()

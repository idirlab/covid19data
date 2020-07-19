from helpers import get_locations,add_locations_header
from datetime import datetime
import codecs
print("Running add_to_time_series.py on "+datetime.now().strftime("%m/%d/%Y %H:%M:%S")+'\n')

countries_file = "../data/input/countries.txt"
counties_file = "../data/input/counties.txt"
states_file = "../data/input/states.txt"

def add_todays_row(time_series_f,temp_csv_f,level,date=None,add_h=False):
    # add_header(level, time_series_f)     #uncomment when creating new time series files
    if add_h:
        add_header(level, time_series_f)
    if not date:
        date = datetime.today().strftime('%Y-%m-%d')    
    time = datetime.now().strftime("%H:%M:%S")

    if level =="s":
        locations = get_locations(states_file)
    elif level == "g":
        locations = get_locations(countries_file)
    elif level == "c":
        locations = get_locations(counties_file)

    with codecs.open(time_series_f,'a', encoding='utf8') as out: #append the new rows to the files
        confirmed = {loc: "NA" for loc in locations}
        deaths = {loc: "NA" for loc in locations}
        recoveries = {loc: "NA" for loc in locations}

        with codecs.open(temp_csv_f,'r',encoding='utf8') as f:  #collecting info from initial files
            source_timestamp = f.readline()
            source_timestamp = source_timestamp.strip()
            out.write('\n' + date + '\t' + time+'\t'+source_timestamp)
            f.readline() # discard the header
            lines=f.readlines()

            for line in lines:
                line= line.strip()
                fields= line.split('\t')
                if fields[0] in confirmed:
                    confirmed[fields[0]]=fields[1]
                    deaths[fields[0]]=fields[2]
                    recoveries[fields[0]]=fields[3]
            f.close()

        for location in locations:  #writing collected data to the series files
            out.write('\t'+confirmed[location]+'-'+deaths[location]+'-'+recoveries[location])
        out.close()

def add_header(level,time_series_file):
    if level == "s":
        add_locations_header(time_series_file,states_file)
    elif level == "c":
        add_locations_header(time_series_file,counties_file)
    elif level == "g":
        add_locations_header(time_series_file,countries_file)

from helpers import get_states,get_counties
from datetime import datetime
import codecs



states= get_states()
counties =get_counties()


def add_todays_row_states(collected_files):
    date = datetime.today().strftime('%Y-%m-%d')
    for file_key, f_path in collected_files.items():
        with codecs.open(f_path+'_time_series.csv','a', encoding='utf8') as out: #append the new rows to the files
            out.write('\n'+date)
            confirmed = {state: "-" for state in states}
            deaths = {state: "-" for state in states}
            recoveries = {state: "-" for state in states}
            with codecs.open(f_path+'.csv','r',encoding='utf8') as f:  #collecting info from initial files
                f.readline()
                lines=f.readlines()
                for line in lines:
                    line= line.strip()
                    fields= line.split('\t')
                    confirmed[fields[0]]=fields[1]
                    deaths[fields[0]]=fields[2]
                    recoveries[fields[0]]=fields[3]
                f.close()

            for state in states:  #writing collected data to the series files
                out.write('\t'+confirmed[state]+'-'+deaths[state]+'-'+recoveries[state])
            out.close()

def add_todays_row_counties(collected_files):
    date = datetime.today().strftime('%Y-%m-%d')
    for file_key, f_path in collected_files.items():
        with codecs.open(f_path+'_time_series.csv','a', encoding='utf8') as out: #append the new rows to the files
            out.write('\n'+date)
            confirmed = {county: "-" for county in counties}
            deaths = {county: "-" for county in counties}
            recoveries = {county: "-" for county in counties}
            with codecs.open(f_path+'.csv','r',encoding='utf8') as f:  #collecting info from initial files
                f.readline()
                lines=f.readlines()
                for line in lines:
                    line= line.strip()
                    fields= line.split('\t')
                    confirmed[fields[0]]=fields[1]
                    deaths[fields[0]]=fields[2]
                    recoveries[fields[0]] = fields[3]
                f.close()

            for county in counties:  #writing collected data to the series files
                out.write('\t'+confirmed[county]+'-'+deaths[county]+'-'+recoveries[county])
            out.close()

if __name__ == '__main__':
    #add_header('../data/COVIDTrackingProject_time_series.csv')  #one time run only to create the header of the file- no need to run it again

    collected_states = {
        "cdc": "../data/cdc",  # be careful with the names as changing them causes the initial .csv files and the time_series .csv file names to change as well
        "cnn": "../data/cnn",
        "NYtimes": "../data/NYtimes",
        "john_hopkins": "../data/johns_hopkins_states",
        "COVIDTrackingProject": "../data/COVIDTrackingProject"
    }

    collected_counties = {
        "john_hopkins": "../data/johns_hopkins_counties"
    }

    try:
        add_todays_row_states(collected_states)
        print("State series collected successfully")
    except Exception as e:
        print(e)

    try:
        add_todays_row_counties(collected_counties)
        print("County Series collected successfully")
    except Exception as e:
        print(e)



from helpers import init_locations,retrieve_data_source,write_temp,abbr_to_state,get_fields_indices_nyt,get_fields_indices_jhu,get_fields_indices_ctp, countyname_mapping
from add_to_time_series import add_header,add_todays_row
import codecs
from datetime import datetime
import pandas as pd
from config_history import *
print("Running collect_data.py on "+datetime.now().strftime("%m/%d/%Y %H:%M:%S")+'\n')
# TODO: modify the value of JHU state before 4.12!!

#############################################

def collect_jhu_c(url,out_f):
    data_source_file = retrieve_data_source(url, "../data/raw/jhu_c.csv")
    deaths, confirmed, recovered = init_locations("c")
    if not data_source_file == "":
        country_field_index, state_field_index, county_field_index, confirmed_field_index, deaths_field_index, recovered_field_index = get_fields_indices_jhu(data_source_file)
        with codecs.open(data_source_file,'r', encoding='utf8') as f:
            f.readline()
            lines = f.readlines()
            for line in lines:
                line= line.strip()
                fields = line.split(',')
                if fields[country_field_index]=='US': #fields[3] is country name
                    county_id = fields[county_field_index].strip() +"-"+fields[state_field_index] #county_id should be in the format "countyName-StateName
                    if county_id in countyname_mapping:
                        county_id = countyname_mapping[county_id]
                    if county_id in confirmed:
                        if fields[confirmed_field_index].strip()=="" : fields[confirmed_field_index]="NA"
                        if fields[deaths_field_index].strip() =="" : fields[deaths_field_index] ="NA"
                        if fields[recovered_field_index].strip()=="": fields[recovered_field_index]="NA"
                        confirmed[county_id]=fields[confirmed_field_index]
                        deaths[county_id]=fields[deaths_field_index]
                        recovered[county_id]=fields[recovered_field_index]

            f.close()
        write_temp(deaths, recovered, confirmed, out_f)
    else:
        print("Data file not found from the source : "+url)

def collect_jhu_s(url,out_f):
    data_source_file = retrieve_data_source(url, "../data/raw/jhu_s.csv")
    deaths, confirmed, recovered = init_locations("s")
    if not data_source_file == "":
        country_field_index, state_field_index, county_field_index, confirmed_field_index, deaths_field_index, recovered_field_index = get_fields_indices_jhu(data_source_file)
        with codecs.open(data_source_file,'r', encoding='utf8') as f:
            f.readline()
            lines = f.readlines()
            for line in lines:
                line= line.strip()
                fields = line.split(',')
                if fields[state_field_index] in confirmed:
                    if fields[confirmed_field_index].strip() == "": fields[confirmed_field_index]="NA"
                    if fields[deaths_field_index].strip() == "":  fields[deaths_field_index] ="NA"
                    if fields[recovered_field_index].strip() =="": fields[recovered_field_index]="NA"
                    confirmed[fields[state_field_index]]=fields[confirmed_field_index]
                    deaths[fields[state_field_index]]=fields[deaths_field_index]
                    recovered[fields[state_field_index]]=fields[recovered_field_index]
            f.close()

        write_temp(deaths, recovered, confirmed, out_f)
    else:
        print("Data file not found from the source : "+url)

def collect_jhu_g(url,out_f):
    data_source_file = retrieve_data_source(url, "../data/raw/jhu_g.csv")
    deaths, confirmed, recovered = init_locations("g")
    if not data_source_file == "":
        country_field_index, state_field_index, county_field_index, confirmed_field_index, deaths_field_index, recovered_field_index = get_fields_indices_jhu(data_source_file)
        with codecs.open(data_source_file, 'r', encoding='utf8') as f:
            f.readline()
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                fields = line.split(',')
                if fields[country_field_index] in confirmed:  # fields[3] is country name
                    if fields[confirmed_field_index] == "" : fields[confirmed_field_index] ="0"
                    if fields[deaths_field_index] =="" : fields[deaths_field_index] ="0"
                    if fields[recovered_field_index] =="" : fields[recovered_field_index] ="0"
                    confirmed[fields[country_field_index]] += int(fields[confirmed_field_index])
                    deaths[fields[country_field_index]] += int(fields[deaths_field_index])
                    recovered[fields[country_field_index]] += int(fields[recovered_field_index])

            f.close()
        write_temp(deaths, recovered, confirmed, out_f)
    else:
        print("Data file not found from the source : "+url)


        
# COVIDTrackingProject: state level
def collect_ctp_s(): #COVID tracking Project
    api_url = 'https://covidtracking.com/api/v1/states/daily.csv'
    df = pd.read_csv(api_url)
    df_out = pd.DataFrame(columns=state_indexes)
    df = df.groupby(['date'])['state', 'positive', 'death'].apply(combine_state).reset_index()
    df.columns = ['date','situation']
    # Insert default value
    for i in state_indexes[3:]:
        df[i] = 'NA-NA-NA'
    new_col = df['situation'].str.split('|', expand=True)
    for idx, row in new_col.iterrows():
        for v in row:
            if v:
                d = v.split('-')
                try:
                    df[ctp_state_mapping[d[0]]].iloc[idx] = '-'.join([d[1], d[2], 'NA'])        
                except:
                    pass                
    df['date'] = df['date'].apply(format_date)
    df['time'] = datetime.now().strftime("%H:%M:%S")
    df['source_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = df.drop(columns=['situation'])
    df = df[state_indexes] # reorder the columns
    df.to_csv("../data/out/ctp_s.csv", sep='\t', index=False)
    
    
    
# NYtimes: state level
def collect_nyt_s():
    api_url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
    df = pd.read_csv(api_url)
    df_out = pd.DataFrame(columns=state_indexes)
    df = df.groupby(['date'])[['state', 'cases', 'deaths']].apply(combine_state).reset_index()
    df.columns = ['date','situation']
    # Insert default value
    for i in state_indexes[3:]:
        df[i] = 'NA-NA-NA'

    new_col = df['situation'].str.split('|', expand=True)

    for idx, row in new_col.iterrows():
        for v in row:
            if v:
                d = v.split('-')
                # 2 special name cases in NYT
                d[0] = 'District Of Columbia' if d[0]=='District of Columbia' else d[0]
                d[0] = 'US Virgin Islands' if d[0]=='Virgin Islands' else d[0]
                try:
                    df[d[0]].iloc[idx] = '-'.join([d[1], d[2], 'NA'])        
                except:
                    # print('can not process {}'.format(d))
                    pass
                    
    df['time'] = datetime.now().strftime("%H:%M:%S")
    df['source_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = df.drop(columns=['situation'])
    df = df[state_indexes] # reorder the columns
    df.to_csv("../data/out/nyt_s.csv", sep='\t', index=False)
    
    
# NYtimes: county level
def collect_nyt_c():
    api_url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
    df = pd.read_csv(api_url)
    df_out = pd.DataFrame(columns=county_indexes)
    df = df.groupby(['date'])[['county', 'state', 'cases', 'deaths']].apply(combine_county).reset_index()
    df.columns = ['date','situation']
    # Insert default value
    for i in county_indexes[3:]:
        df[i] = 'NA-NA-NA'

    new_col = df['situation'].str.split('|', expand=True)
    can_not = set()

    for idx, row in new_col.iterrows():
        for v in row:
            if v:
                d = v.split('-')
                if len(d)==4: 
                    countyName = '-'.join([d[0], d[1]])
                    if countyName in df.columns:
                        df[countyName].iloc[idx] = '-'.join([d[2], d[3], 'NA'])
                    else:
                        try:
                            df[countyname_mapping[countyName]].iloc[idx] = '-'.join([d[2], d[3], 'NA'])
                        except:
                            can_not.add(countyName)
                elif len(d)==5: # There are some county name
                    countyName = '-'.join([d[0], d[1], d[2]])
                    if countyName in df.columns:
                        df[countyName].iloc[idx] = '-'.join([d[3], d[4], 'NA'])
                    else:
                        try:
                            df[countyname_mapping[countyName]].iloc[idx] = '-'.join([d[3], d[4], 'NA'])
                        except:
                            can_not.add(countyName)
                    
                      
    df['time'] = datetime.now().strftime("%H:%M:%S")
    df['source_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = df.drop(columns=['situation'])
    df = df[county_indexes] # reorder the columns
    
    df.to_csv("../data/out/nyt_c.csv", sep='\t', index=False)




if __name__ == '__main__':

    # data sources urls
    JohnsHopkins_counties_global_url ="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"
    JohnsHopkins_states_url =  "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/"
    NYTimes_url_states = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/live/us-states.csv"
    COVIDTrackingProject_url = "https://covidtracking.com/api/states.csv"
    NYTimes_url_counties = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/live/us-counties.csv"
    # output temporary files (not time series)

    jhu_global = "../data/temp/jhu_g.csv"
    jhu_counties = "../data/temp/jhu_c.csv"
    jhu_states = "../data/temp/jhu_s.csv"
    nyt_counties = "../data/temp/nyt_c.csv"
    nyt_states = "../data/temp/nyt_s.csv"
    ctp_states = "../data/temp/ctp_s.csv"
    jhu_time_series_g = "../data/out/jhu_g.csv"
    jhu_time_series_s = "../data/out/jhu_s.csv"
    jhu_time_series_c = "../data/out/jhu_c.csv"
    nyt_time_series_s = "../data/out/nyt_s.csv"
    nyt_time_series_c = "../data/out/nyt_c.csv"
    cpt_time_series_s = "../data/out/ctp_s.csv"

    # date = datetime.today().strftime('%m-%d-%Y')  # date format should be : e.g.:03-26-2020.csv
    dates = pd.date_range('1/22/2020','7/16/2020')
    # add_header(level, time_series_f)     #uncomment when creating new time series files
    for i, date in enumerate(dates):
        url_date = date.strftime('%m-%d-%Y')
        try:
            url = JohnsHopkins_counties_global_url + url_date + '.csv'
            collect_jhu_c(url,jhu_counties)
            print("JHU counties data collected successfully !")
            if i==0:
                add_todays_row(jhu_time_series_c, jhu_counties, "c", date.strftime('%Y-%m-%d'), add_h=True)
            else:
                add_todays_row(jhu_time_series_c, jhu_counties, "c", date.strftime('%Y-%m-%d'))
        except Exception as e:
            print(e)
        try:
            url = JohnsHopkins_states_url + url_date + '.csv'
            collect_jhu_s(url,jhu_states)
            print("JHU state data collected successfully !")
            if i==0:
                add_todays_row(jhu_time_series_s, jhu_states, "s", date.strftime('%Y-%m-%d'), add_h=True)
            else:
                add_todays_row(jhu_time_series_s, jhu_states, "s", date.strftime('%Y-%m-%d'))
        except Exception as e:
            print(e)
        try:
            url = JohnsHopkins_counties_global_url + url_date + '.csv'
            collect_jhu_g(url,jhu_global)
            print("JHU global data collected successfully !")
            if i==0:
                add_todays_row(jhu_time_series_g, jhu_global, "g", date.strftime('%Y-%m-%d'), add_h=True)
            else:
                add_todays_row(jhu_time_series_g, jhu_global, "g", date.strftime('%Y-%m-%d'))
        except Exception as e:
            print(e)


    try:
        collect_nyt_s()
        print("NY Times state data collected successfully !")
    except Exception as e:
        print(e)
        
    try:
        collect_nyt_c()
        print("NY Times county data collected successfully !")
    except Exception as e:
        print(e)

    try:
        collect_ctp_s()
        print("COVID Tracking Project's data collected successfully !")
    except Exception as e:
        print(e)

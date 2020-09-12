import optparse
from collections import OrderedDict
import os
from helpers import init_locations,retrieve_data_source,write_temp,abbr_to_state,get_fields_indices_nyt,get_fields_indices_jhu,get_fields_indices_ctp, countyname_mapping
from add_to_time_series import add_header,add_todays_row
import codecs
from datetime import datetime, timedelta
print("Running collect_data.py on "+datetime.now().strftime("%m/%d/%Y %H:%M:%S")+'\n')

def parse_parameters(opts):
    param = OrderedDict()
    param['jhu'] = opts.jhu
    param['nyt'] = opts.nyt
    param['ctp'] = opts.ctp
    param['date'] = opts.date
    param['yesterday'] = opts.yesterday
    return param

#############################################
def collect_nyt(url,output_file,level):
    data_source_file = retrieve_data_source(url,"../data/raw/nyt_"+level+".csv")
    deaths, confirmed, recovered = init_locations(level)
    if not data_source_file == "":
        state_field_index, county_field_index, confirmed_field_index, deaths_field_index = get_fields_indices_nyt(data_source_file)
        with codecs.open(data_source_file,'r',encoding='utf8') as tempf:
            tempf.readline()
            lines = tempf.readlines()
            for line in lines:
                line = line.strip()
                fields = line.split(',')
                if level =="s":
                    location = fields[state_field_index]
                else:
                    location = fields[county_field_index].strip()+'-'+fields[state_field_index]
                    if location in countyname_mapping:
                        location = countyname_mapping[location]
                if location in confirmed:
                    if fields[confirmed_field_index].strip() == "": fields[confirmed_field_index] = "NA"
                    if fields[deaths_field_index].strip() == "": fields[deaths_field_index] = "NA"
                    confirmed[location] = fields[confirmed_field_index]
                    deaths[location] =fields[deaths_field_index]
                    recovered[location] ="NA"
            write_temp(deaths, recovered, confirmed, output_file)
    else:
        print("Data file not found from the source : "+url)



def collect_jhu_c(url,out_f):
    file_date = url[-14:-6]
    date_ = datetime.strptime(file_date, '%m-%d-%y')
    file_date = date_.strftime('%Y-%m-%d')

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
        write_temp(deaths, recovered, confirmed, out_f, file_date)
        return True
    else:
        print("Data file not found from the source : "+url)
        return False

def collect_jhu_s(url,out_f):
    file_date = url[-14:-6]
    date_ = datetime.strptime(file_date, '%m-%d-%y')
    file_date = date_.strftime('%Y-%m-%d')

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

        write_temp(deaths, recovered, confirmed, out_f,file_date)
        return True
    else:
        print("Data file not found from the source : " + url)
        return False

def collect_jhu_g(url,out_f):
    file_date = url[-14:-6]
    date_ = datetime.strptime(file_date, '%m-%d-%y')
    file_date = date_.strftime('%Y-%m-%d')

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
        write_temp(deaths, recovered, confirmed, out_f,file_date)
        return True
    else:
        print("Data file not found from the source : " + url)
        return False


def collect_ctp(url,output_file):  #COVID tracking Project
    data_source_file = retrieve_data_source(url, '../data/raw/ctp_s.csv')
    deaths, confirmed, recovered = init_locations("s")
    if not data_source_file == "":
        location_field_index, confirmed_field_index, deaths_field_index = get_fields_indices_ctp(data_source_file)
        with codecs.open(data_source_file, 'r', encoding='utf8') as f:
            f.readline()
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                fields = line.split(',')
                if fields[location_field_index] in abbr_to_state:
                    if fields[confirmed_field_index].strip() == '': fields[confirmed_field_index]="NA"  # some fields come empty from the file and replace the initial 0 value
                    if fields[deaths_field_index].strip() == '': fields[deaths_field_index] = "NA"
                    confirmed[abbr_to_state[fields[location_field_index]]] = fields[confirmed_field_index]  # convert the postal abbreviation of states to full state name
                    deaths[abbr_to_state[fields[location_field_index]]] = fields[deaths_field_index]
                    recovered[abbr_to_state[fields[location_field_index]]] = "NA"
            f.close()
        write_temp(deaths, recovered, confirmed, output_file)
    else:
        print("Data file not found from the source : "+url)



def main(opts):
    params= parse_parameters(opts)
    time = datetime.now().strftime("%H:%M:%S")
    print (params)
    # data sources urls
    JohnsHopkins_counties_global_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"
    JohnsHopkins_states_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/"
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
    if params['jhu']:
        try:
            url = JohnsHopkins_counties_global_url + params['date'] + '.csv'
            success = collect_jhu_c(url, jhu_counties)
            if success:
                print("JHU counties data collected successfully !")
                add_todays_row(jhu_time_series_c, jhu_counties, "c",params['date'],time)
            else:
                print("Collecting the most recent file instead...")
                url = JohnsHopkins_counties_global_url + params['yesterday'] + '.csv'
                success = collect_jhu_c(url, jhu_counties)
                if success:
                    print("JHU counties data collected successfully !")
                    add_todays_row(jhu_time_series_c, jhu_counties, "c",params['date'],time)
        except Exception as e:
            print(e)
        try:
            url = JohnsHopkins_states_url + params['date'] + '.csv'
            success = collect_jhu_s(url, jhu_states)
            if success:
                print("JHU state data collected successfully !")
                add_todays_row(jhu_time_series_s, jhu_states, "s",params['date'],time)
            else:
                print("Collecting the most recent file instead...")
                url = JohnsHopkins_states_url + params['yesterday'] + '.csv'
                success = collect_jhu_s(url, jhu_states)
                if success:
                    print("JHU state data collected successfully !")
                    add_todays_row(jhu_time_series_s, jhu_states, "s",params['date'],time)
        except Exception as e:
            print(e)
        try:
            url = JohnsHopkins_counties_global_url + params['date'] + '.csv'
            success = collect_jhu_g(url, jhu_global)
            if success:
                print("JHU global data collected successfully !")
                add_todays_row(jhu_time_series_g, jhu_global, "g",params['date'],time)
            else:
                print("Collecting the most recent file instead...")
                url = JohnsHopkins_counties_global_url + params['yesterday'] + '.csv'
                success = collect_jhu_g(url, jhu_global)
                if success:
                    print("JHU global data collected successfully !")
                    add_todays_row(jhu_time_series_g, jhu_global, "g",params['date'],time)
        except Exception as e:
            print(e)
    if params['ctp']:
        try:
            collect_ctp(COVIDTrackingProject_url, ctp_states)
            print("COVID Tracking Project's data collected successfully !")
            add_todays_row(cpt_time_series_s, ctp_states, "s",params['date'],time)
        except Exception as e:
            print(e)
    if params['nyt']:
        try:
            collect_nyt(NYTimes_url_states, nyt_states, "s")
            print("NY Times state data collected successfully !")
            add_todays_row(nyt_time_series_s, nyt_states, "s",params['date'],time)
        except Exception as e:
            print(e)
        try:
            collect_nyt(NYTimes_url_counties, nyt_counties, "c")
            print("NY Times county data collected successfully !")
            add_todays_row(nyt_time_series_c, nyt_counties, "c",params['date'],time)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    today = datetime.today().strftime('%m-%d-%Y')  # date format should be : e.g.:03-26-2020.csv
    yesterday = datetime.strftime(datetime.now() - timedelta(1), '%m-%d-%Y')  # subtracting one day from today's date
    optparser = optparse.OptionParser()

    optparser.add_option(
        "-j", "--jhu", default=True, dest='jhu', action="store_true", help="if set,  collects jhu data")
    optparser.add_option(
        "-n", "--nyt", default=True, dest='nyt', action="store_true", help="if set, collects nyt data")
    optparser.add_option(
        "-c", "--ctp", default=True, dest='ctp', action="store_true", help="if set, collects ctp data")
    optparser.add_option(
        "-d", "--date", default=today, help="set the date in the format MM-dd-yyyy for which you wish to collect data")
    optparser.add_option(
        "-y", "--yesterday", default=yesterday, help="the day before the date specified in the date paramater in the format MM-dd-yyyy")

    opts = optparser.parse_args()[0]

    main(opts)


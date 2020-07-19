import codecs
import requests
from datetime import datetime

def get_locations(locations_file):
    locations=[]
    with codecs.open(locations_file,'r',encoding='utf8') as f:
        lines = f.readlines()
        for line in lines:
            line =line.strip()
            if locations_file.endswith("counties.txt"):
                fields = line.split(',')
                loc = fields[1]+'-'+fields[2]
            else:
                loc = line
            locations.append(loc)
        f.close()
    return locations


def abbrev_to_state(abbrev_file):
    abbr_2_state = dict()
    with codecs.open(abbrev_file,'r',encoding='utf8') as f:
        lines = f.readlines()
        for line in lines:
            line=line.strip()
            fields = line.split(',')
            abbr_2_state[fields[0]] = fields[1]
        f.close()
    return abbr_2_state




def get_provinces(provinces_file):
    provinces =[]
    with codecs.open(provinces_file,'r',encoding='utf8') as f:
        lines = f.readlines()
        for line in lines:
            line=line.strip()
            provinces.append(line)
        f.close()
    return provinces

def add_locations_header(output_file,locations_file):
    locations = get_locations(locations_file)
    with codecs.open(output_file,'w',encoding='utf8') as out:
        out.write("date\ttime\tsource_timestamp")
        for loc in locations:
            out.write('\t'+loc)
        out.close()



#this is a one time execution function
def sum_provinces(provinces_file):
    with codecs.open(provinces_file,'r',encoding='utf8') as f:
        f.readline()
        lines = f.readlines()
        for line in lines:
            deaths = 0
            confirmed = 0
            recoveries = 0
            line=line.strip()
            fields = line.split('\t')[3:]
            for field in fields:
                temp = field.split('-')
                confirmed+= int(temp[0])
                deaths += int(temp[1])
                if temp[2]=='NA':
                    r = 0
                else:
                    r = temp[2]
                recoveries += int(r)
            print(str(confirmed)+'-'+str(deaths)+'-'+str(recoveries))

def write_temp(deaths,recoveries,confirmed,out_file):
    with codecs.open(out_file, 'w', encoding='utf8') as out:
        out.write(timedate_stamp + '\n')
        out.write("LOCATION\tCASES\tDEATHS\tRECOVERED\n")
        for key, val in confirmed.items():
            out.write(key + '\t' + str(val)+ '\t' + str(deaths[key]) + '\t' + str(recoveries[key]) + '\n')
        out.close()

def init_locations(level):
    if level =="s":
        locations = states
    elif level == "c":
        locations = counties
    elif level == "g":
        locations = countries
    deaths =  {loc:0 for loc in locations} #initialize a new dict with states as keys and values as zeros
    confirmed = {loc:0 for loc in locations}
    recovered = {loc:0 for loc in locations}
    return deaths,confirmed,recovered

def retrieve_data_source(url,raw_f):
    r = requests.get(url, allow_redirects=True)
    if r.status_code == 200:  # if the file is found and exists in the repsonse (404 status code means file not found)
        open(raw_f, 'wb').write(r.content)  # write the file to local machine
        return raw_f
    else:
        return ""


def get_fields_indices_nyt(data_source_f):
    state_field_index =-1
    county_field_index =-1
    confirmed_field_index=-1
    deaths_field_index=-1
    with codecs.open(data_source_f, 'r', encoding='utf8') as f:
        line = f.readline()
        line =line.strip()
        fields = line.split(',')
        for i,field in enumerate(fields):
            if field =="state":
                state_field_index=i
            elif field =="county":
                county_field_index = i
            elif field == "cases":
                confirmed_field_index = i
            elif field == "deaths":
                deaths_field_index = i
        f.close()
    return state_field_index, county_field_index, confirmed_field_index, deaths_field_index

def get_fields_indices_ctp(data_source_f):
    location_field_index=-1
    confirmed_field_index=-1
    deaths_field_index=-1
    with codecs.open(data_source_f, 'r', encoding='utf8') as f:
        line = f.readline()
        line = line.strip()
        fields = line.split(',')
        for i, field in enumerate(fields):
            if field == "state":
                location_field_index = i
            elif field == "positive":
                confirmed_field_index = i
            elif field == "death":
                deaths_field_index = i
        f.close()
    return location_field_index, confirmed_field_index, deaths_field_index

def get_fields_indices_jhu(data_source_f):
    state_field_index=-1
    county_field_index =-1
    country_field_index = -1
    confirmed_field_index=-1
    deaths_field_index=-1
    recovered_field_index =-1
    with codecs.open(data_source_f, 'r', encoding='utf8') as f:
        line = f.readline()
        line =line.strip()
        fields = line.split(',')
        for i,field in enumerate(fields):
            if field =="Province_State":
                state_field_index=i
            elif field =="Country_Region":
                country_field_index = i
            elif field =="Admin2":
                county_field_index = i
            elif field == "Confirmed":
                confirmed_field_index = i
            elif field == "Deaths":
                deaths_field_index = i
            elif field == "Recovered":
                recovered_field_index = i
        f.close()
    return country_field_index, state_field_index, county_field_index, confirmed_field_index, deaths_field_index, recovered_field_index



states= get_locations("../data/input/states.txt")
abbr_to_state= abbrev_to_state("../data/input/state_abbrev.txt")
counties = get_locations("../data/input/counties.txt")
countries = get_locations("../data/input/countries.txt")
date = datetime.today().strftime('%Y-%m-%d')
time = datetime.now().strftime("%H:%M:%S")
timedate_stamp = date + " " + time

# sum_provinces("../data/canada_time_series_tsv.csv")
# DO NOT REMOVE THESE COMMENT LINES !!!
# add_header_global("../data/JHU_global_time_series_wto_province_413_israa.csv")
# add_header_states("../data/cdc_time_series.csv")
# add_header_states("../data/cnn_time_series.csv")
# add_header_states("../data/NYtimes_time_series.csv")
# add_header_states("../data/johns_hopkins_states_time_series.csv")
# add_header_states("../data/COVIDTrackingProject_time_series.csv")
# add_header_counties("../data/johns_hopkins_counties_time_series.csv")

countyname_mapping = {'DeKalb-Indiana': 'De Kalb-Indiana', 
                 'DeSoto-Florida': 'De Soto-Florida', 
                 'DuPage-Illinois': 'Du Page-Illinois', 
                 'St. Clair-Missouri': 'St Clair-Missouri', 
                 'Portsmouth city-Virginia': 'Portsmouth City-Virginia', 
                 'Lynchburg city-Virginia': 'Lynchburg City-Virginia', 
                 'Staunton city-Virginia': 'Staunton City-Virginia', 
                 'Buena Vista city-Virginia': 'Buena Vista City-Virginia',
                 'Winchester city-Virginia': 'Winchester City-Virginia', 
                 'St. Clair-Michigan': 'St Clair-Michigan', 
                 'Manassas Park city-Virginia': 'Manassas Park City-Virginia', 
                 'St. Clair-Alabama': 'St Clair-Alabama', 
                 'Kodiak Island Borough-Alaska': 'Kodiak Island-Alaska', 
                 'DeKalb-Tennessee': 'De Kalb-Tennessee', 
                 'Dillingham Census Area-Alaska': 'Dillingham-Alaska', 
                 'DeKalb-Illinois': 'De Kalb-Illinois', 
                 'Hopewell city-Virginia': 'Hopewell City-Virginia', 
                 'St. Croix-Wisconsin': 'St Croix-Wisconsin', 
                 'St. Helena-Louisiana': 'St Helena-Louisiana', 
                 'Bethel Census Area-Alaska': 'Bethel-Alaska', 
                 'St. Louis city-Missouri': 'St Louis-Missouri', 
                 'Emporia city-Virginia': 'Emporia City-Virginia',
                 'Manassas city-Virginia': 'Manassas City-Virginia', 
                 'Wrangell City and Borough-Alaska': 'Wrangell-Petersburg-Alaska', 
                 'Lexington city-Virginia': 'Lexington City-Virginia', 
                 'St. Landry-Louisiana': 'St Landry-Louisiana', 
                 'Lake and Peninsula Borough-Alaska': 'Lake and Peninsula-Alaska', 
                 'Suffolk city-Virginia': 'Suffolk City-Virginia', 
                 'St. Louis-Minnesota': 'St Louis-Minnesota', 
                 'St. Charles-Louisiana': 'St Charles-Louisiana',
                 'St. Joseph-Indiana': 'St Joseph-Indiana', 
                 'Radford city-Virginia': 'Radford City-Virginia',
                 "O'Brien-Iowa": "O Brien-Iowa", 
                 'Galax city-Virginia': 'Galax City-Virginia',
                 'North Slope Borough-Alaska': 'North Slope-Alaska', 
                 "St. Mary's-Maryland": "St. Mary's-Maryland", 
                 'District of Columbia-District of Columbia': 'Washington-District of Columbia', 
                 'Virginia Beach city-Virginia': 'Virginia Beach City-Virginia', 
                 'Fairbanks North Star Borough-Alaska': 'Fairbanks North Star-Alaska', 
                 "Queen Anne's-Maryland": "Queen Annes-Maryland", 
                 'Aleutians East Borough-Alaska': 'Aleutians East Borough-Alaska', 
                 'LaGrange-Indiana': 'La Grange-Indiana', 
                 'Alexandria city-Virginia': 'Alexandria City-Virginia', 
                 'St. Lawrence-New York': 'St Lawrence-New York', 
                 'St. Clair-Illinois': 'St Clair-Illinois', 
                 'Matanuska-Susitna Borough': 'Matanuska-Susitna-Alaska', 
                 'Norfolk city-Virginia': 'Norfolk City-Virginia', 
                 'Roanoke city-Virginia': 'Roanoke City-Virginia', 
                 'Falls Church city-Virginia': 'Falls Church City-Virginia',
                 'Franklin city-Virginia': 'Franklin City-Virginia', 
                 'Fairfax city-Virginia': 'Fairfax City-Virginia', 
                 'DeSoto-Mississippi': 'De Soto-Mississippi', 
                 'Yukon-Koyukuk Census Area-Alaska': 'Yukon-Koyukuk-Alaska', 
                 'Colonial Heights city-Virginia': 'Colonial Heights Cit-Virginia', 
                 'Bristol Bay Borough-Alaska': 'Bristol Bay-Alaska', 
                 'St. Charles-Missouri': 'St Charles-Missouri', 
                 'Newport News city-Virginia': 'Newport News City-Virginia', 
                 'St. Louis-Missouri': 'St Louis-Missouri', 
                 'Richmond city-Virginia': 'Richmond City-Virginia', 
                 'Ketchikan Gateway Borough-Alaska': 'Ketchikan Gateway-Alaska', 
                 'DeWitt-Texas': 'De Witt-Texas', 
                 'Danville city-Virginia': 'Danville City-Virginia', 
                 'Salem city-Virginia': 'Salem City-Virginia', 
                 "Prince George's-Maryland": "Prince Georges-Maryland", 
                 'Harrisonburg city-Virginia': 'Harrisonburg City-Virginia',
                 'Sitka City and Borough-Alaska': 'Sitka-Alaska', 
                 'St. Tammany-Louisiana': 'St Tammany-Louisiana', 
                 'DeKalb-Georgia': 'De Kalb-Georgia', 
                 'St. John the Baptist-Louisiana': 'St John the Baptist-Louisiana', 
                 'Charlottesville city-Virginia': 'Charlottesville City-Virginia', 
                 'Petersburg city-Virginia': 'Petersburg City-Virginia', 
                 'Covington city-Virginia': 'Covington City-Virginia', 
                 'LaSalle-Louisiana': 'La Salle-Louisiana', 
                 'Chesapeake city-Virginia': 'Chesapeake City-Virginia', 
                 'Kenai Peninsula Borough-Alaska': 'Kenai Peninsula-Alaska', 
                 'Northwest Arctic Borough-Alaska': 'Northwest Arctic-Alaska',
                 'LaPorte-Indiana': 'La Porte-Indiana', 
                 'St. Joseph-Michigan': 'St Joseph-Michigan', 
                 'St. Francis-Arkansas': 'St Francis-Arkansas', 
                 'St. James-Louisiana': 'St James-Louisiana', 
                 'Baltimore city-Maryland': 'Baltimore City-Maryland', 
                 'New York City-New York': 'New York-New York', 
                 'LaSalle-Illinois': 'La Salle-Illinois', 
                 'St. Martin-Louisiana': 'St Martin-Louisiana', 
                 'Williamsburg city-Virginia': 'Williamsburg City-Virginia', 
                 'Waynesboro city-Virginia': 'Waynesboro City-Virginia', 
                 'St. Johns-Florida': 'St Johns-Florida', 
                 'Haines Borough-Alaska': 'Haines-Alaska', 
                 'Southeast Fairbanks Census Area-Alaska': 'Southeast Fairbanks-Alaska', 
                 'DeKalb-Missouri': 'De Kalb-Missouri', 
                 'Aleutians West Census Area-Alaska': 'Aleutians West-Alaska', 
                 'DeKalb-Alabama': 'De Kalb-Alabama', 
                 'Poquoson city-Virginia': 'Poquoson City-Virginia', 
                 'Juneau City and Borough-Alaska': 'Juneau-Alaska', 
                 'Norton city-Virginia': 'Norton City-Virginia', 
                 'St. Francois-Missouri': 'St Francois-Missouri', 
                 'Petersburg Borough-Alaska':'Wrangell-Petersburg-Alaska', 
                 'St. Lucie-Florida': 'St Lucie-Florida', 
                 'Doña Ana-New Mexico': 'Dona Ana-New Mexico', 
                 'St. Bernard-Louisiana': 'St Bernard-Louisiana', 
                 'Hampton city-Virginia': 'Hampton City-Virginia', 
                 'Fredericksburg city-Virginia': 'Fredericksburg City-Virginia', 
                 'Bristol city-Virginia': 'Bristol City-Virginia', 
                 'Valdez-Cordova Census Area-Alaska': 'Valdez-Cordova-Alaska', 
                 'St. Mary-Louisiana': 'St Mary-Louisiana', 
                 'Nome Census Area-Alaska': 'Nome-Alaska',
                 'Miami-Dade-Florida': 'Dade-Florida',
                 'Matanuska-Susitna Borough-Alaska': 'Matanuska-Susitna-Alaska', 
                 'Denali Borough-Alaska': 'Denali-Alaska', 
                 'Aleutians East Borough-Alaska': 'Aleutians East-Alaska',
                 'Prince of Wales-Hyder Census Area-Alaska': 'Prince of Wales-Outer Ketchikan-Alaska', 
                 }
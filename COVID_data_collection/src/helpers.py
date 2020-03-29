import codecs

def get_countries():
    countries=[]
    with codecs.open("../data/countries.txt",'r',encoding='utf8') as f:
        lines = f.readlines()
        for line in lines:
            line=line.strip()
            countries.append(line)
        f.close()
    return countries


def abbrev_to_state():
    abbr_2_state = dict()
    with codecs.open("../data/state_abbrev.txt",'r',encoding='utf8') as f:
        lines = f.readlines()
        for line in lines:
            line=line.strip()
            fields = line.split(',')
            abbr_2_state[fields[0]] = fields[1]
        f.close()
    return abbr_2_state


def get_states():
    states =[]
    with codecs.open("../data/states.txt",'r',encoding='utf8') as f:
        lines = f.readlines()
        for line in lines:
            line=line.strip()
            states.append(line)
        f.close()
    return states

def get_counties():
    counties = []
    with codecs.open("../data/counties.txt",'r',encoding='utf8') as f:
        lines = f.readlines()
        for line in lines:
            line=line.strip()
            fields = line.split(',')
            id = fields[1]+'-'+fields[-1]
            counties.append(id)
        f.close()
    return counties



def add_header_global(output_file):
    countries = get_countries()
    with codecs.open(output_file,'w',encoding='utf8') as out:
        out.write("date")
        for country in countries:
            out.write('\t'+country)
        out.close()

def add_header_states(output_file):
    states = get_states()
    with codecs.open(output_file,'w',encoding='utf8') as out:
        out.write("date\t")
        for state in states:
            out.write(state+'\t')
        out.close()

def add_header_counties(output_file):
    counties = get_counties()
    with codecs.open(output_file,'w',encoding='utf8') as out:
        out.write("date\t")
        for county in counties:
            out.write(county+'\t')
        out.close()

# DO NOT REMOVE THESE COMMENT LINES !!!
#add_header_global("../data/JHU_global_time_series.csv")
# add_header_states("../data/cdc_time_series.csv")
# add_header_states("../data/cnn_time_series.csv")
# add_header_states("../data/NYtimes_time_series.csv")
# add_header_states("../data/johns_hopkins_states_time_series.csv")
# add_header_states("../data/COVIDTrackingProject_time_series.csv")
# add_header_counties("../data/johns_hopkins_counties_time_series.csv")

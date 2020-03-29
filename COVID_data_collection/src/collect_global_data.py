from helpers import get_countries
import requests
from datetime import datetime
import codecs
from helpers import get_countries


def get_JohnHopkins_data(url_confirm,url_death,output_file):

    # the data from john hopkins come in separate files for the cases and the deaths
    r = requests.get(url_confirm, allow_redirects=True)
    open('../data/raw_JH_confirmed_global.csv', 'wb').write(r.content)
    r = requests.get(url_death, allow_redirects=True)
    open('../data/raw_JH_death_global.csv', 'wb').write(r.content)

    countries = get_countries()
    confirmed = {country:"0" for country in countries}
    deaths = {country:"0" for country in countries}

    with codecs.open('../data/raw_JH_confirmed_global.csv','r', encoding='utf8') as f1:
        f1.readline()
        lines = f1.readlines()
        for line in lines:
            line= line.strip()
            fields = line.split(',')
            if fields[0].strip()=='':
                confirmed[fields[1]] = fields[-1]
            else:
                confirmed[fields[1]+' - '+fields[0]]=fields[-1]
        f1.close()

    with codecs.open('../data/raw_JH_death_global.csv','r', encoding='utf8') as f2:  # lazy !
        f2.readline()
        lines = f2.readlines()
        for line in lines:
            line= line.strip()
            fields = line.split(',')
            if fields[0].strip()=='':
                deaths[fields[1]] = fields[-1]
            else:
                deaths[fields[1]+' - '+fields[0]]=fields[-1]
        f2.close()

    countries = get_countries()

    with codecs.open(output_file, 'a', encoding='utf8') as out:
        date = datetime.today().strftime('%Y-%m-%d')
        out.write('\n'+date)
        for country in countries:
            out.write('\t'+confirmed[country]+'-'+deaths[country]+'-'+'NA')
        out.close()




if __name__ == '__main__':


    JohnHopkins_deaths_url ="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
    JohnHopkins_confirmed_url="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"


    try:
        get_JohnHopkins_data(JohnHopkins_confirmed_url, JohnHopkins_deaths_url, '../data/JHU_global_time_series.csv')
        print("Johns Hopkins' global data collected successfully !")
    except Exception as e:
        print(e)


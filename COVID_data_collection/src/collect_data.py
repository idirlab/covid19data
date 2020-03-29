# for scraping, I am using Selenium because the pages I want to scrape contain dynamic elements that are geenerated when certain scripts run (e.g a button click handler)
# selenium provides methods to execute these scripts and generate the elements I need.
# these scrapers are used to collect data for the state and county level

from helpers import get_states,abbrev_to_state,get_counties
import codecs
from datetime import datetime
from selenium import webdriver
#from selenium.webdriver import Chrome

import requests
#import logging
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True
#options.executable_path ='../geckodriver'
driver = webdriver.Firefox(executable_path='../geckodriver',options=options)



#webdriver = "../chromedriver"  # the relative path of the browser driver (the file "chromedriver") to simulate a user who uses a browser #you can use Firefox driver too
#webdriver = "../geckodriver"

#driver = Chrome(webdriver)
#driver = webdriver.Firefox(executable_path='../geckodriver')

states= get_states()
abbr_to_state= abbrev_to_state()
counties = get_counties()

def scrape_NY_times(url,output_file):
    death_cases =  {state:"0" for state in states} #initialize a new dict with states as keys and values as zeros
    confirmed = {state:"0" for state in states}

    driver.get(url)
    cases_by_state_dev = driver.find_element_by_id('g-cases-by-state') #getting the dev that has the tbale of cases: it contains a button that when clicked shows more tuples from the table
    #collapse_overlayMessage_button = driver.find_element_by_xpath('//button[@data-testid="expanded-dock-btn-selector"]')
    #collapse_overlayMessage_button.click()
    showMore_button = cases_by_state_dev.find_element_by_tag_name('button') #getting the button "Show more" to click it and generate all the tuples of the table
    driver.execute_script("arguments[0].click();", showMore_button)  #executing the script associated with clicking the button
    #showMore_button.click()  #can also be done this way but if there is an overlay or anything in the way it crashes #clicking the button to show more tuples
    rows = cases_by_state_dev.find_elements_by_tag_name('tr')  #getting all the rows (tr elements ) (tuples) of the table inside the parent dev

    for row in rows:
        row_text = row.text
        row_text = row_text.strip()
        fields = row_text.split(' ')
        if not fields[1].isnumeric() and len(fields)==4: #e.g. New York 3 500
            state_name = fields[0]+" "+fields[1]
            confirmed[state_name] = fields[2]
            death_cases[state_name]=fields[-1]
        elif not fields[1].isnumeric() and not fields[2].isnumeric() and len(fields)==5: # e.g. District of Columbia 5 300
            state_name = fields[0] +" "+ fields[1] + " "+fields[2]
            confirmed[state_name] = fields[3]
            death_cases[state_name] = fields[-1]
        else:  #e.g. Texas 5 400
            state_name= fields[0]
            confirmed[state_name] = fields[1]
            death_cases[state_name] = fields[-1]

        with codecs.open(output_file, 'w', encoding='utf8') as out:
            out.write("COUNTY\tCASES\tDEATHS\tRECOVERED\n")
            for key, val in confirmed.items():
                out.write(key + '\t' + val + '\t' + death_cases[key] + '\t' + 'NA' + '\n')
            out.close()



def scrape_CNN(url,output_file):

    driver.get(url)
    driver.implicitly_wait(10) #wainting 10 seconds to ensure the dynamic elements are visible and can be located by the web driver
    showMore_button = driver.find_element_by_class_name('region-table-toggle')  # getting the button "Show more" to click it and generate all the tuples of the table
    #showMore_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.class, "myDynamicElement")) #waits 10 seconds until it the dynamic element is located (visible)
    driver.execute_script("arguments[0].click();",showMore_button)  # executing the script associated with clicking the button
    driver.implicitly_wait(10)
    read_all_container = driver.find_element_by_class_name('region-table-list')
    table_body = read_all_container.find_element_by_tag_name('tbody')
    rows = table_body.find_elements_by_tag_name('tr')
    death_cases =  {state:"0" for state in states} #initialize a new dict with states as keys and values as zeros
    confirmed = {state:"0" for state in states}
    for r in rows:
        fields = r.find_elements_by_tag_name('td')
        state_name = fields[0].text.strip()
        if state_name in states:
            confirmed[state_name] = fields[1].text
            death_cases[state_name]= fields[2].text


    with codecs.open(output_file,'w',encoding='utf8') as out:
        out.write("COUNTY\tCASES\tDEATHS\tRECOVERED\n")
        for key,val in confirmed.items():
            out.write(key+'\t'+val+'\t'+death_cases[key]+'\t'+'NA'+'\n')
        out.close()


def get_JohnsHopkins_data(url,output_file_states,output_file_counties):
    # check if today's data fila under dailr reports folder is available
    date = datetime.today().strftime('%m-%d-%Y') #date format should be : e.g.:03-26-2020.csv
    #date = '03-27-2020'
    url = url+date+'.csv'
    r = requests.get(url, allow_redirects=True)
    if r.status_code ==200:  # if the file is found and exists in the repsonse (404 status code means file not found)
        open('../data/raw_JH.csv', 'wb').write(r.content)  #write the file to local machine

        confirmed_states= {state:0 for state in states}
        deaths_states = {state:0 for state in states}
        recovered_satates ={state:0 for state in states}
        confirmed_counties = {county:"0" for county in counties}
        deaths_counties = {county:"0" for county in counties}
        recovered_counties = {county: "0" for county in counties}

        with codecs.open('../data/raw_JH.csv','r', encoding='utf8') as f:
            f.readline()
            lines = f.readlines()
            for line in lines:
                line= line.strip()
                fields = line.split(',')
                if fields[3]=='US': #fields[3] is country name
                    if fields[2] in states:     # fields[2] is state name
                        confirmed_states[fields[2]]+=int(fields[7])  #fields[7] is number of confirmed cases
                        deaths_states[fields[2]] += int(fields[8])   #fields[8] is number of deaths
                        recovered_satates[fields[2]] += int(fields[9])  #fields[9] is number of recovered
                        combined_key_elements = fields[-3].strip()+"-"+fields[-2].strip()  #fields[-1] is a combined key in the format "Abbeville, South Carolina, US"
                        county_id= combined_key_elements.replace('\"','')   #county_id should be in the format "countyName-StateName"

                        if county_id in counties:
                            confirmed_counties[county_id]=fields[7]
                            deaths_counties[county_id]=fields[8]
                            recovered_counties[county_id]=fields[9]

            f.close()

        with codecs.open(output_file_states, 'w', encoding='utf8') as out:
            out.write("STATE\tCASES\tDEATHS\tRECOVERED\n")
            for key,val in confirmed_states.items():
                out.write(key+'\t'+str(val)+'\t'+str(deaths_states[key])+'\t'+str(recovered_satates[key])+'\n')
            out.close()

        with codecs.open(output_file_counties, 'w', encoding='utf8') as out:
            out.write("COUNTY\tCASES\tDEATHS\tRECOVERED\n")
            for key,val in confirmed_counties.items():
                out.write(key+'\t'+val+'\t'+deaths_counties[key]+'\t'+recovered_counties[key]+'\n')
            out.close()


def get_COVID_tracking_project_data(url,output_file):
    r = requests.get(url, allow_redirects=True)
    open('../data/raw_COVIDTrackingProject.csv', 'wb').write(r.content)
    confirmed= {state:"0" for state in states}
    deaths = {state:"0" for state in states}
    with codecs.open('../data/raw_COVIDTrackingProject.csv','r',encoding='utf8') as f:
        f.readline()
        lines= f.readlines()
        for line in lines:
            line=line.strip()
            fields = line.split(',')
            if fields[0] in abbr_to_state:
                if not fields[1].strip()=='':  # some fields come empty from the file and replace the initial 0 value
                    confirmed[abbr_to_state[fields[0]]] = fields[1]   # convert the postal abbreviation of states to full state name
                else:
                    confirmed[abbr_to_state[fields[0]]] = "NA"
                if not fields[4].strip()=='':
                    deaths[abbr_to_state[fields[0]]] = fields[11]
                else:
                    deaths[abbr_to_state[fields[0]]] = "NA"
        f.close()
    with codecs.open(output_file,'w',encoding='utf8') as out:
        out.write("COUNTY\tCASES\tDEATHS\tRECOVERED\n")
        for key,val in confirmed.items():
            out.write(key+'\t'+val+'\t'+deaths[key]+'\t'+'NA'+'\n')
        out.close()


def scrape_CDC_data(url,output_file):
    confirmed = {state: "0" for state in states}
    driver.get(url)
    driver.implicitly_wait(10)
    table_section = driver.find_element_by_class_name('data-table')
    driver.implicitly_wait(10)
    collapse_button = table_section.find_element_by_xpath('//div[@tabindex="0"]')
    driver.execute_script("arguments[0].click();", collapse_button)
    table_dev = driver.find_element_by_class_name ('rt-tbody') #getting the table
    row_devs = table_dev.find_elements_by_class_name('rt-tr-group') #getting the rows

    for row_dev in row_devs:
        field_devs = row_dev.find_elements_by_class_name('rt-td')
        dev_text = field_devs[0].text # in every table row there are four cells, the first one carries the state name in a <span> , and the others have the number of cases, death, directly in their .text property
        splitted = dev_text.split("\n")
        state_name= splitted[0]
        confirmed_cases= field_devs[1].text
        if confirmed_cases=='None':     # replace the word none by the number 0
            confirmed_cases='0'
        confirmed[state_name]=confirmed_cases

    with codecs.open(output_file,'w',encoding='utf8') as out:
        out.write("COUNTY\tCASES\tDEATHS\tRECOVERED\n")
        for key, val in confirmed.items():
            out.write(key + '\t' + val + '\t' + 'NA'+ '\t' + 'NA' + '\n')
        out.close()



if __name__ == '__main__':


    JohnsHopkins_url ="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"
    CNN_url = "https://www.cnn.com/2020/03/03/health/us-coronavirus-cases-state-by-state/index.html"
    NYTimes_url = "https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html"
    COVIDTrackingProject_url = "https://covidtracking.com/api/states.csv"
    CDC_url="https://www.cdc.gov/TemplatePackage/contrib/widgets/cdcMaps/build/index.html?chost=www.cdc.gov&cpath=/coronavirus/2019-ncov/cases-updates/cases-in-us.html&csearch=CDC_AA_refVal%3Dhttps%253A%252F%252Fwww.cdc.gov%252Fcoronavirus%252F2019-ncov%252Fcases-in-us.html&chash=&ctitle=Cases%20in%20U.S.%20%7C%20CDC&wn=cdcMaps&wf=/TemplatePackage/contrib/widgets/cdcMaps/build/&wid=cdcMaps1&mMode=widget&mPage=&mChannel=&class=mb-3&host=www.cdc.gov&theme=theme-cyan&configUrl=/coronavirus/2019-ncov/map-cases-us.json"


    try:
        scrape_NY_times(NYTimes_url, '../data/NYtimes.csv')
        print("NT Times' data collected successfully !")
    except Exception as e:
        print(e)

    try:
        scrape_CNN(CNN_url,'../data/cnn.csv')
        print("CNN's data collected successfully !")
    except Exception as e:
        print(e)

    try:
        scrape_CDC_data(CDC_url,'../data/cdc.csv')
        print("CDC's data collected successfully !")
    except Exception as e:
        print(e)

    try:
        get_JohnsHopkins_data(JohnsHopkins_url, '../data/johns_hopkins_states.csv','../data/johns_hopkins_counties.csv')
        print("Johns Hopkins' data collected successfully !")
    except Exception as e:
        print(e)

    try:
        get_COVID_tracking_project_data(COVIDTrackingProject_url,'../data/COVIDTrackingProject.csv')
        print("COVID Tracking Project's data collected successfully !")
    except Exception as e:
        print(e)


    driver.quit()  # closes all the browser windows opened by this program.
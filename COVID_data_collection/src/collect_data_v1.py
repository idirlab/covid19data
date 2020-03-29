# for scraping, I am using Selenium because the pages I want to scrape contain dynamic elements that are geenerated when certain scripts run (e.g a button click handler)
# selenium provides methods to execute these scripts and generate the elements I need.
import codecs
from selenium import webdriver
#from selenium.webdriver import Chrome
import requests
from word2number import w2n
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

states = ['Alabama','Alaska','Arizona','Arkansas','California', 'Colorado','Connecticut','Delaware', 'District of Columbia','Florida',
          'Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts',
          'Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York',
          'North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Puerto Rico','Rhode Island','South Carolina','South Dakota',
          'Tennessee','Texas','US Virgin Islands','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming']

abbr_to_state= {'AL':'Alabama','AS':'Alaska','AZ':'Arizona','AK':'Arkansas','CA':'California', 'CO':'Colorado','CT':'Connecticut','DE':'Delaware', 'DC':'District of Columbia','FL':'Florida',
          'GA':'Georgia','HI':'Hawaii','ID':'Idaho','IL':'Illinois','IN':'Indiana','IA':'Iowa','KS':'Kansas','KY':'Kentucky','LA':'Louisiana','ME':'Maine','MD':'Maryland','MA':'Massachusetts',
          'MI':'Michigan','MN':'Minnesota','MS':'Mississippi','MO':'Missouri','MT':'Montana','NE':'Nebraska','NV':'Nevada','NH':'New Hampshire','NJ':'New Jersey','NM':'New Mexico','NY':'New York',
          'NC':'North Carolina','ND':'North Dakota','OH':'Ohio','OK':'Oklahoma','OR':'Oregon','PA':'Pennsylvania','PR':'Puerto Rico','RI':'Rhode Island','SC':'South Carolina','SD':'South Dakota',
          'TN':'Tennessee','TX':'Texas','VI':'US Virgin Islands','UT':'Utah','VT':'Vermont','VA':'Virginia','WA':'Washington','WV':'West Virginia','WI':'Wisconsin','WY':'Wyoming'}

def scrape_NY_times(url,output_file):

    driver.get(url)
    cases_by_state_dev = driver.find_element_by_id('g-cases-by-state') #getting the dev that has the tbale of cases: it contains a button that when clicked shows more tuples from the table
    #collapse_overlayMessage_button = driver.find_element_by_xpath('//button[@data-testid="expanded-dock-btn-selector"]')
    #collapse_overlayMessage_button.click()
    showMore_button = cases_by_state_dev.find_element_by_tag_name('button') #getting the button "Show more" to click it and generate all the tuples of the table
    driver.execute_script("arguments[0].click();", showMore_button)  #executing the script associated with clicking the button
    #showMore_button.click()  #can also be done this way but if there is an overlay or anything in the way it crashes #clicking the button to show more tuples
    rows = cases_by_state_dev.find_elements_by_tag_name('tr')  #getting all the rows (tr elements ) (tuples) of the table inside the parent dev
    with codecs.open(output_file, 'w',encoding='utf8') as out:
        for row in rows:
            row_text = row.text
            row_text = row_text.strip()
            fields = row_text.split(' ')
            if not fields[1].isnumeric() and len(fields)==4: #e.g. New York 3 500
                out.write(fields[0]+" "+fields[1]+'\t'+fields[2]+'\t'+fields[-1]+'\n')
            elif not fields[1].isnumeric() and not fields[2].isnumeric() and len(fields)==5: # e.g. District of Columbia 5 300
                out.write(fields[0] +" "+ fields[1] + " "+fields[2] + '\t' + fields[3]+ '\t' + fields[-1] + '\n')
            else:
                out.write(fields[0] + '\t' + fields[1] + '\t' + fields[-1] + '\n') #e.g. Texas 5 400

        out.close()




def scrape_CNN(url,output_file):

    driver.get(url)
    #1: get the number of deaths and active cases
    read_all_container = driver.find_element_by_class_name('zn-body__read-all')
    paragraphs = read_all_container.find_elements_by_class_name('zn-body__paragraph')
    death_cases =  {state:"0" for state in states} #initialize a new dict with states as keys and values as zeros
    confirmed = {state:"0" for state in states}
    for p in paragraphs:
        text = p.text.strip()
        fields = text.split(':')
        if fields[0] in states:
            fields[-1]=fields[-1].strip()
            confirmed[fields[0]]= fields[-1].strip()
            if "including" in p.text:
                confirmed[fields[0]] = fields[-1][: fields[-1].index(" (including")]
                deaths = fields[-1][fields[-1].index("including ") + len("including "): fields[-1].index(" death")] #gets the number of cases from the string (e.g. "California: 596 (including 14 deaths)" )
                if not deaths.isnumeric():
                    deaths = str(w2n.word_to_num(deaths))
                death_cases[fields[0]]= deaths

                ##### OLD CNN PAGE (keep just in case they return the table and the map)
    #2: get the number of active cases
    # covid_embed_dev = driver.find_element_by_id('responsive-embed-20200306-us-covid19') #grabs the dev that has the iframe of the data (map+table)
    # iframe = covid_embed_dev.find_elements_by_tag_name('iframe')[0] #grabing the iframe that has the table inside
    # driver.switch_to_frame(iframe)
    # #embedded_html = driver.find_element_by_tag_name('html')
    # embed_dev_table = driver.find_element_by_id('graphic') #grabs the dev that has the table of data
    # rows = embed_dev_table.find_elements_by_class_name('row') #grabs the rows of the table (the table is not HTML table, it is a set of devs)


    # with codecs.open(output_file, 'w', encoding='utf8') as out:
    #     out.write("STATE\tCASES\tDEATHS\n")
    #     # for row in rows:
    #     #     row_text = row.text
    #     #     row_text = row_text.strip()
    #     #     fields = row_text.split('\n')
    #     deaths = death_cases[fields[0]]
    #     out.write(fields[0]+'\t'+fields[-1]+'\t'+deaths+'\n')
    #
    #     out.close()
    with codecs.open(output_file,'w',encoding='utf8') as out:
        out.write("STATE\tCASES\tDEATHS\n")
        for key,val in confirmed.items():
            out.write(key+'\t'+val+'\t'+death_cases[key]+'\n')
        out.close()


def get_JohnHopkins_data(url_confirm,url_death,output_file):
    # the data from john hopkins come in separate files for the cases and the deaths
    r = requests.get(url_confirm, allow_redirects=True)
    open('../data/raw_JH_confirmed.csv', 'wb').write(r.content)
    r = requests.get(url_death, allow_redirects=True)
    open('../data/raw_JH_death.csv', 'wb').write(r.content)

    confirmed= {state:"0" for state in states}
    deaths = {state:"0" for state in states}
    with codecs.open('../data/raw_JH_confirmed.csv','r', encoding='utf8') as f1:
        lines = f1.readlines()
        for line in lines:
            line= line.strip()
            fields = line.split(',')
            if fields[1]=='US':
                if fields[0] in states:
                    confirmed[fields[0]]=fields[-1]
        f1.close()
    with codecs.open('../data/raw_JH_death.csv','r', encoding='utf8') as f2:  # lazy !
        lines = f2.readlines()
        for line in lines:
            line= line.strip()
            fields = line.split(',')
            if fields[1]=='US':
                if fields[0] in states:
                    deaths[fields[0]]=fields[-1]
        f2.close()
    with codecs.open(output_file, 'w', encoding='utf8') as out:
        out.write("STATE\tCASES\tDEATHS\n")
        for key,val in confirmed.items():
            out.write(key+'\t'+val+'\t'+deaths[key]+'\n')
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
                if not fields[4].strip()=='':
                    deaths[abbr_to_state[fields[0]]] = fields[4]
        f.close()
    with codecs.open(output_file,'w',encoding='utf8') as out:
        out.write("STATE\tCASES\tDEATHS\n")
        for key,val in confirmed.items():
            out.write(key+'\t'+val+'\t'+deaths[key]+'\n')
        out.close()


def scrape_CDC_data(url,output_file):
    confirmed = {state: "0" for state in states}
    driver.get(url)
    #table_section = driver.find_element_by_class_name('data-table')
    collapse_button = driver.find_element_by_class_name('data-table-heading')#if the class name has two classes, give the last part as argument here (e.g. this dev has two classes "collapsed data-table-heading", we only gave "data-table-heading" as argument)
    driver.execute_script("arguments[0].click();", collapse_button)
    table_dev = driver.find_element_by_class_name ('rt-tbody') #getting the table
    row_devs = table_dev.find_elements_by_class_name('rt-tr-group') #getting the rows

    for row_dev in row_devs:
        field_devs = row_dev.find_elements_by_class_name('rt-td')
        dev_text = field_devs[0].text # in every table row there are four cells, the first one carries the state name in a <span> , and the others have the number of cases, death, directly in their .text property
        splitted = dev_text.split("\n")
        state_name= splitted[0]
        confirmed_cases= field_devs[2].text
        if confirmed_cases=='None':     # replace the word none by the number 0
            confirmed_cases='0'
        confirmed[state_name]=confirmed_cases

    with codecs.open(output_file,'w',encoding='utf8') as out:
        out.write("STATE\tCASES\tDEATHS\n")
        for key, val in confirmed.items():
            out.write(key + '\t' + val + '\t' + '-' + '\n')
        out.close()




    # Selenium quick tutorial:
    #finding all elements that belong to a class:
    #driver.find_elements_by_class_name("quote")
    # find one element by a class name and getting the content text
    #quote.find_element_by_class_name('text').text
    #finding an element by ID
    #login_form = driver.find_element_by_id('loginForm')








    #Beautiful soup quick tutorial:
    # Beautiful soup won't work because parts of the page is dynamic (for instance, a button to "show more" tuples from the cases table in new york times
    #page = requests.get(url)
    #soup = BeautifulSoup(page.content, 'html.parser')
    #get an element by its ID
    #results = soup.find(id='g-cases-by-state')
    # get all elements whose tag is 'section' and whose class is 'card content'
    #job_elems = results.find_all('section', class_='card-content')
    #print the text inside an element
    #print(title_elem.text)
    #find element by class name and text inside it
    #python_jobs = results.find_all('h2', string='Python Developer')
    #Extract Attributes From HTML Elements
    #link = elementvariable.find('a')['href'] # gets the attribute href's value from the tag <a> (the element stored in var. elementvariable
    #Pass a Function to a Beautiful Soup Method
    #passing an anonymous function to the string= argument. The lambda function looks at the text of each <h2> element,
    #converts it to lowercase, and checks whether the substring 'python' is found anywhere in there.
    #python_jobs = results.find_all('h2',string=lambda text: 'python' in text.lower())

if __name__ == '__main__':


    #JohnHopkins_deaths_url ="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"
    #JohnHopkins_confirmed_url="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
    JohnsHopkins_url ="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"
    CNN_url = "https://www.cnn.com/2020/03/03/health/us-coronavirus-cases-state-by-state/index.html"
    NYTimes_url = "https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html"
    COVIDTrackingProject_url = "https://covidtracking.com/api/states.csv"
    CDC_url="https://www.cdc.gov/TemplatePackage/contrib/widgets/cdcMaps/build/index.html?chost=www.cdc.gov&cpath=/coronavirus/2019-ncov/cases-updates/cases-in-us.html&csearch=CDC_AA_refVal%3Dhttps%253A%252F%252Fwww.cdc.gov%252Fcoronavirus%252F2019-ncov%252Fcases-in-us.html&chash=&ctitle=Cases%20in%20U.S.%20%7C%20CDC&wn=cdcMaps&wf=/TemplatePackage/contrib/widgets/cdcMaps/build/&wid=cdcMaps1&mMode=widget&mPage=&mChannel=&class=mb-3&host=www.cdc.gov&theme=theme-cyan&configUrl=/coronavirus/2019-ncov/map-cases-us.json"

    # try:
    #     scrape_NY_times(NYTimes_url, '../data/NYtimes.csv')
    #     print("NT Times' data collected successfully !")
    # except Exception as e:
    #     print(e)
    #
    # try:
    #     scrape_CNN(CNN_url,'../data/cnn.csv')
    #     print("CNN's data collected successfully !")
    # except Exception as e:
    #     print(e)

    try:
        scrape_CDC_data(CDC_url,'../data/cdc.csv')
        print("CDC's data collected successfully !")
    except Exception as e:
        print(e)

    try:
        get_JohnHopkins_data(JohnsHopkins_url, '../data/john_hopkins.csv')
        print("John Hopkins' data collected successfully !")
    except Exception as e:
        print(e)

    try:
        get_COVID_tracking_project_data(COVIDTrackingProject_url,'../data/COVIDTrackingProject.csv')
        print("COVID Tracking Project's data collected successfully !")
    except Exception as e:
        print(e)


    driver.quit()  # closes all the browser windows opened by this program.
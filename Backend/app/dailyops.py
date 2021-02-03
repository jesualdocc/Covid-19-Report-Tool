import os
import joblib
from predictions_and_analysis.predictor import Covid_Predictor
from db.sql_connector import DbManagement

####################################################
def update_globe_data():
    #Cache data for globe (Threejs)
    print('-------------------------- UPDADING GLOBE DATA -----------------------------')

    #Establish conection to db 
    sql = DbManagement()
    j = 0
    while True:
        j = j + 1
        try:
            #name, hasmore, population, latitude, longitude
            countries = sql.get_all_countries()
            
            data = []
            total = len(countries)
            for i, c in enumerate(countries):
                
                if c[0] == 'US':
                ##US has county level data
                    #Get overral country data first
                    tmp = sql.get_info(country = c[0], days=1)
                    if not tmp:
                        #Empty Dictionary 
                        continue
                    
                    ret_dict = create_dict(res_dict=tmp, country=c[0], state=None, county=None, population=c[2], latitude=c[3], longitude=c[4])
                    data.append(ret_dict)
                    
                    #Get county level data
                    usa = sql.get_all_state_county()  # state, county, latitude, longitude
                    
                    for res in usa:
                    #res => res[0] - state, res[1] - county, res[2] - population, res[3] - latitude, res[4] -longitude
                        tmp = sql.get_info(country = c[0], state = res[0], county = res[1], days=1)
                        if not tmp:
                            #Empty Dictionary 
                            continue
                        ret_dict = create_dict(res_dict=tmp, country=c[0], state=res[0], county=res[1], population=res[2], latitude=res[3], longitude=res[4])
                        data.append(ret_dict)
                        
                elif c[1] == 1 or c[1] == 2:
                ##Countries with State/Province or other Territories data
                    #Get overall/main country data first
                    tmp = sql.get_info(country = c[0], days=1)
                    if not tmp:
                        #Empty Dictionary
                        continue
                    
                    ret_dict = create_dict(res_dict=tmp, country=c[0], state=None, county=None, population=c[2], latitude=c[3], longitude=c[4])
                    data.append(ret_dict)

                    #Get State/Province or other Territories data after
                    prov_states = sql.get_country_provs_states(country=c[0])

                    for ps in prov_states:

                        tmp = sql.get_info(country = c[0], state=ps[0], days=1)
                        if not tmp:
                            #Empty Dictionary 
                            continue
                        ret_dict = create_dict(res_dict=tmp, country=c[0], state=ps[0], county=None, population=c[2], latitude=ps[1], longitude=ps[2])
                        data.append(ret_dict)

                else:
                    #All other countries
                    tmp = sql.get_info(country = c[0], days=1)
                    if not tmp:
                        #Empty Dictionary 
                        continue
                    
                    ret_dict = create_dict(res_dict=tmp, country=c[0], state=None, county=None, population=c[2], latitude=c[3], longitude=c[4])
                    data.append(ret_dict)
                    
                print('\r' + ' ' + str(i + 2) + ' of ' + str(total) + ' updated ', end='\r')

            #Get Overall world data
            tmp = sql.get_info(days=1)
            if tmp:
                #Has data Dictionary
                ret_dict = create_dict(res_dict=tmp, country='World', state=None, county=None, population=0, latitude=0, longitude=0)
                data.append(ret_dict) 
            
            
            dirname = os.path.dirname(__file__)
            filename = os.path.join(dirname, 'routes/GlobeData')
            joblib.dump(data, filename) #Save data for regular use (avoid multiple db calls)
            print('-------------------------- DONE UPDADING GLOBE DATA -----------------------------')

        except Exception as e:
            sql.connect_to_db()
            if j > 5:
                return


def create_dict(res_dict, country, state, county, population, latitude, longitude):
    date = list(res_dict.keys())[0]
    values = list(res_dict.values())[0] #cases, deaths

    values['country'] = country
    values['state']  = state
    values['county'] = county
    values['population'] = population
    values['latitude'] = latitude
    values['longitude'] = longitude
    values['last_update'] = date

    return values

#############################################

def model_training():
    #Function to perform training for each county
    
    #Establish conection to db 
    sql = DbManagement() 
    j = 0
    while True:
        j = j + 1
        try:
            usa_result = sql.get_all_state_county()
            world_result = sql.get_all_countries()
            
            #Usa
            print('-------------------------- PERFORMING USA MODELS TRAINING -----------------------------')

            total = len(usa_result)
            #Overall country first
            covid_predictor = Covid_Predictor(sql, country='US', state =None, county =None)
            covid_predictor.train_models()

            for i, res in enumerate(usa_result):
                #(sql, county, state)
                covid_predictor = Covid_Predictor(sql, country='US', state =res[0], county =res[1])
                covid_predictor.train_models()
                print('\r' + ' ' + str(i + 2) + ' of ' + str(total) + ' models trained ', end='\r')
        

            print('-------------------------- PERFORMING WORLD MODELS TRAINING -----------------------------')
            total = len(world_result)
            for i, c in enumerate(world_result):
                if c[1] == 1:
                ##Countries with State/Province or other Territories data
                    #Country first
                    covid_predictor = Covid_Predictor(sql, country= c[0], state =None, county =None)
                    covid_predictor.train_models()
                    prov_states = sql.get_country_provs_states(c[0])

                    for ps in prov_states:
                        #State/Province or other Territories after
                        covid_predictor = Covid_Predictor(sql, country= c[0], state =ps[0], county =None)
                        covid_predictor.train_models()

                else:
                    #All other countries
                    covid_predictor = Covid_Predictor(sql, country= c[0], state =None, county =None)
                    covid_predictor.train_models()
                
                print('\r' + ' ' + str(i + 2) + ' of ' + str(total) + ' models trained ', end='\r')

            print('-------------------------- DONE TRAINING MODELS -----------------------------')
            return
        
        except Exception as e:
            sql.connect_to_db()
            if j > 5:
                return

################################################         
def get_latest_data():
    #Get daily update
        #Establish conection to db 
    sql = DbManagement() 
    i = 0 
    while True:
        i = i + 1
        try:
            sql.update_db() #Latest data
            return
        except Exception as e:
            sql.connect_to_db()
            if i > 5:
                return

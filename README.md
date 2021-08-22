# Challenge
 Jobsity data engineer challenge
 
 It has two apis developed with Python Flask and both return JSON responses.
 
 - api_load_data has two endpoints: 
   * weekly_average in /api/weekly_average - METHOD: GET : this endpoint, is callable from postman with the following configuration:
     In body tab, in raw data, in JSON format, you have to send three arguments:
       - list : list of point of polygon, optional
       - region : name of the region of a trip, optional
       Minimun it needs one of the argurments before.
       - day_week : day in the week used to calculate the week, and then with that, filter the trips in the week adition to the list of points or region filter, to calculate the weekly average.

     Example of body JSON with full arguments:      
              {
                  "list" : [ "POINT (14.5197800 49.6582031)",
                              "POINT (1.0546279 73.9599609)",
                              "POINT (19.4355143 71.5869141)",
                              "POINT (20.3034175 54.3164063)",
                              "POINT (14.5197800 49.4824219)" ],
                  "region" : "Prague",
                  "day_week" : "2021-08-20"
              }
   
   
   * save_csv in /api/trips_save  - METHOD: POST : this endpoint is callable from postman with the following configuration:
     In body tab, in form-data, in KEY goes "file" and in value have to load the csv file.
     This process load the csv file into the database in a trip table. Also, group trips for hour and minute and for distance between origins and destionations, and take as similar trip who has at 100km at least. This is the process that uses most of the time in this method.
     
     This solution is scalable, but with more time, it is posible to improve performance, and use threads to process in parallel or improve the performance of the algorithm to detect points nearby. I probe until 100 thousand of registers and the time to process that file was about two hours. With more memory the process can load more registers and process them. Also, I understand that I used the same dataset and replicated multiples times to obtain 100 thousand of registers and I had a lot of trips similars that add a lot of processing and not represents the reality of the distribution of the trips.
     
     
 - api_status hay one endpoint:
   * csv_file_status in  /api/csv_file_status - METHOD: GET  : this endpoint this endpoint is callable from postman with only the url and tells the status of the data ingestion with a percentage between 0 and 100.
   
   
  
 In each api, exists a readme to help to config and run it.
     
 
 This project use POSTGRESQL as database, so you have to configure the variables to connect the api to the database.

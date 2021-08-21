# Challenge
 Jobsity data engineer challenge
 
 It has two apis developed with Python Flask and both return JSON responses.
 
 - api_load_data has two endpoints: 
   * weekly_average in /api/weekly_average - METHOD: GET : this endpoint, is callable from postman with the following configuration:
     In body tab, raw data, in JSON format, it is posible to send three arguments:
       - list : list of point of polygon, optional
       - region : name of the region of a trip, optional
       Minimun it needs one of the argurments before.
       - day_week : day in the week used to calculate the week, and then with the week, filter the trips in that week to calculate the weekly average in adition to the list or                         region filter.

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
     In body tab, form-data, in KEY goes "file" and in value have to load the csv file.
     This process load the csv file into the database in a trip table. Also, group trips for hour and minute and for distance between origins and destionations, 
     

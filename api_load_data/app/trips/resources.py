import io
import json
import csv
from datetime import datetime, timedelta, date

from flask import request, Blueprint
from flask_restful import Api, Resource

from .schemas import CsvFileSchema, TripSchema, RegionSchema, DatasourceSchema, SimilarTripsSchema
from ..models.models import CsvFile, Trip, SimilarTrips, Datasource, Region
from ..support.haversine import Haversine
from ..support.point import Point

challenge = Blueprint('challenge', __name__)

csv_file_schema = CsvFileSchema()
trip_schema = TripSchema()
region_schema = RegionSchema()
datasource_schema = DatasourceSchema()
similar_trips_schema = SimilarTripsSchema()


api = Api(challenge)


class Trips(Resource):
    # parameter to define the distance between trips in order to consider them similar. Represents kilometers(km)
    _PARAM_SIMILARITY = 10

    @classmethod
    def set_up(cls):
        SimilarTrips.query.delete()
        Trip.query.delete()
        Datasource.query.delete()
        Region.query.delete()

    def get(self):
        trips = Trip.get_all()
        return trip_schema.dump(trips, many=True)

    # method to process the csv datafile
    def post(self):

        # delete the data from all tables
        Trips.set_up()

        # read csv file sent
        file = request.files['file']
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)

        # convert csv file in list
        trips_list = list(csv_input)

        # load file
        file = CsvFile(name=file.name, trip_count=len(trips_list), trip_similar_keys=0, processed_trips_count_list=0,
                       processed_trips_count_similar=0, process_start_date=datetime.today(),
                       process_end_date_list=None, process_end_date=None)
        file_id = file.save()

        Trips.load_datasources_regions(trips_list, file_id)
        # Load Regions and Datasources from the csv file list
        return '{ "success": true , "results": "Process Done"}'

    @classmethod
    def load_datasources_regions(cls, trips, file_id):
        first_row = True
        datasource = []
        region = []
        for row in trips:
            if first_row:
                first_row = False
            else:
                datasource.append(row[4])
                region.append(row[0])
        region_set = set(region)
        datasource_set = set(datasource)

        reg_insert = []
        for region in region_set:
            reg = Region(name=region)
            reg_insert.append(reg)
        Region.save_all(reg_insert)

        datasource_insert = []
        for datasource in datasource_set:
            ds = Datasource(name=datasource)
            datasource_insert.append(ds)
        Datasource.save_all(datasource_insert)

        '''
        Creates a dictionary : key (hour and minute) : values = [Trip,..] to group trips with the same hour and minute.
        Also inserts all Trips in the database
        '''
        diccionary = Trips.process_trip_list(trips, file_id)

        '''
        With Haversine's algorithm, the dictionary is read by taking each key from the dictionary and the trips for 
        each key, and with that the distance between each trip is calculated. Then those with distance less than 
        _PARAM_SIMILARITY are assigned as similar trips. 
        '''
        Trips.process_similarity(diccionary, Trips._PARAM_SIMILARITY, file_id)

    @classmethod
    def process_trip_list(cls, trips_list, file_id):
        trip_id = 0
        first_row = True
        dictionary = {}
        count = 0
        trips = []
        for trip_csv in trips_list:
            count += 1
            if first_row:
                first_row = False
            else:
                trip_id += 1
                date = datetime.strptime(str(trip_csv[3]).strip(), '%Y-%m-%d %H:%M:%S')
                hour_minute = str(date.hour) + ':' + str(date.minute)

                trip = Trip(trip_id=trip_id, region_id=Region.find_by_name(trip_csv[0]), origin_latitude=Point(trip_csv[1]).latitude,
                            origin_longitude=Point(trip_csv[1]).longitude,
                            destination_latitude=Point(trip_csv[2]).latitude,
                            destination_longitude=Point(trip_csv[2]).longitude, date=date,
                            datasource_id=Datasource.find_by_name(trip_csv[4]))
                trips.append(trip)
                #trip.save()
                # db.session.add(trip)
                # db.session.commit()
                if hour_minute in dictionary:
                    dictionary[hour_minute].append(trip)
                else:
                    dictionary[hour_minute] = [trip]

            if count % 10000 == 0:
                Trip.bulk_save(trips)
                trips.clear()
                CsvFile.save_proccess_status_list(count, file_id, 0)
        Trip.bulk_save(trips)
        trips.clear()
        CsvFile.save_proccess_status_list(count, file_id, len(dictionary))
        return dictionary

    @classmethod
    def process_similarity(cls, dictionary, param_similarity, file_id):
        count = 0
        for key in dictionary:
            count += 1
            lista_values = dictionary[key]
            similar_trips = []
            for trip in lista_values:

                similar_origin = list(filter(
                    lambda c: Haversine.calculate_distance(float(c.origin_latitude), float(c.origin_longitude),
                                                           float(lista_values[0].origin_latitude),
                                                           float(lista_values[0].origin_longitude)) <= param_similarity,
                    lista_values))
                similar_destination = list(filter(
                    lambda c: Haversine.calculate_distance(float(c.destination_latitude),
                                                           float(c.destination_longitude),
                                                           float(similar_origin[0].destination_latitude),
                                                           float(similar_origin[
                                                                     0].destination_longitude)) <= param_similarity,
                    similar_origin))

                for sim in similar_destination:
                    if sim.trip_id != trip.trip_id:
                        similar_trip = SimilarTrips(trip_id=trip.trip_id, similar_trip_id=sim.trip_id)
                        similar_trips.append(similar_trip)
                        # similar_trip.save()
                        # # db.session.add(similar_trip)
                        # # db.session.commit()

            SimilarTrips.bulk_save(similar_trips)
            similar_trips.clear()
            CsvFile.save_proccess_status_similar(count, file_id)

        CsvFile.save_proccess_status_similar(count, file_id )


class TripList(Resource):
    '''
    Method that expects a json with tree different attributes:
        day_week : a date used to calculate the begginig and the end of the week and with that dates obtain trips
                    beetwen. If date is not sent, the date used in this method is today
        list : with a list of points to find trips inside that list
        region : with a name of a region to find trips for that region
    '''

    def get(self):
        not_point_list = False
        not_region = False

        dic = request.json
        try:
            day_week = datetime.strptime(str(dic['day_week']).strip(), '%Y-%m-%d')
        except Exception as e:
            day_week = date.today()

        try:
            points = dic['list']
        except Exception as e:
            points = None
            not_point_list = True

        try:
            region = dic['region']
        except Exception as e:
            region = None
            not_region = True

        if not_region & not_point_list:
            return '{ "Result": "Did not send properties list or region"}'

        start = day_week - timedelta(days=day_week.weekday())
        end = start + timedelta(days=6)

        average = TripList.search_by_points_or_region(start, end, points, region)

        return '{ "Weekly_average": ' + str(average) + '}'

    @classmethod
    def search_by_points_or_region(cls, start_date, end_date, points, region):
        trips_inside = []
        print(start_date)
        print(end_date)
        if region:
            region_trips = Trip.find_trips_in_week(region, start_date, end_date)
            trips = region_trips
        else:
            trips = Trip.get_all_in_week(start_date, end_date)

        if points:
            for trip in trips:
                if trip.is_inside(points):
                    trips_inside.append(trip)
        else:
            trips_inside = trips

        return TripList.calculate_weekly_average(trips_inside)

    '''
        method that expects the trip list in one week.
        The average is the trip count for the week divided into seven 
    '''

    @classmethod
    def calculate_weekly_average(cls, trips):
        return len(trips) / 7


api.add_resource(TripList, '/api/weekly_average', endpoint='weekly_average')
api.add_resource(Trips, '/api/trips_save', endpoint='save_csv')

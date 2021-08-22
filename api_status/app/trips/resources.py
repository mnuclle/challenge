from flask import request, Blueprint
from flask_restful import Api, Resource

from .schemas import CsvFileSchema
from ..models.models import CsvFile

challenge = Blueprint('challenge', __name__)

csv_file_schema = CsvFileSchema()

api = Api(challenge)



class CsvFileResource(Resource):

    '''
    After many processed files, I get a percentage of the time that consumes each process:
       the insert of trips
       the process of similarities and insert of similar trips
    and this percentages are used to calculate the percentage/status of the file upload
    '''

    _LIST_PERCENTAGE = 0.3
    _SIMILAR_PERCENTAGE = 0.7


    def get(self):
        csv_file = CsvFile.get_all()
        csvf = csv_file[-1]

        trip_count = csvf.trip_count
        trip_similar_keys = csvf.trip_similar_keys
        processed_trips_count_list = csvf.processed_trips_count_list
        processed_trips_count_similar = csvf.processed_trips_count_similar

        '''
        trip_count --> _LIST_PERCENTAGE %
        processed_trips_count_list   --> processed_trips_count_list * _LIST_PERCENTAGE / trip_count
        '''

        if trip_count != processed_trips_count_list:
            percentage_advance = (processed_trips_count_list * CsvFileResource._LIST_PERCENTAGE) / trip_count
        else:
            '''
            trip_similar_keys --> _SIMILAR_PERCENTAGE %
            processed_trips_count_similar   --> processed_trips_count_similar * _SIMILAR_PERCENTAGE / trip_similar_keys
            '''
            print(processed_trips_count_similar)
            print(CsvFileResource._SIMILAR_PERCENTAGE)
            print(trip_similar_keys)
            print((processed_trips_count_similar * CsvFileResource._SIMILAR_PERCENTAGE))
            print((processed_trips_count_similar * CsvFileResource._SIMILAR_PERCENTAGE)
                  / trip_similar_keys)

            percentage_advance = 0.3 + ((processed_trips_count_similar * CsvFileResource._SIMILAR_PERCENTAGE)
                                        / trip_similar_keys)

        percentage_advance = round(percentage_advance * 100, 2)
        result = '{"percentage_advance": ' + str(percentage_advance) + '}'
        return result


api.add_resource(CsvFileResource, '/api/csv_file_status', endpoint='csv_file_status')

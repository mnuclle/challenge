from marshmallow import fields
from app.ext import ma


class TripSchema(ma.Schema):
    trip_id = fields.Integer(dump_only=True)
    origin_latitude = fields.String()
    origin_longitude = fields.String()
    destination_latitude = fields.String()
    destination_longitude = fields.String()
    date = fields.DateTime()
    datasource_id = fields.Integer()
    region_id = fields.Integer()


class SimilarTripsSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    trip_id = fields.Integer()
    similar_trip_id = fields.Integer()


class RegionSchema(ma.Schema):
    region_id = fields.Integer(dump_only=True)
    name = fields.String()
    trips = fields.Nested('TripSchema', many=True)


class DatasourceSchema(ma.Schema):
    datasource_id = fields.Integer(dump_only=True)
    name = fields.String()
    datasource_trips = fields.Nested('TripSchema', many=True)


class CsvFileSchema(ma.Schema):
    file_id = fields.Integer(dump_only=True)
    name = fields.String()
    trip_count = fields.Integer()
    trip_similar_keys = fields.Integer()
    processed_trips_count_list = fields.Integer()
    processed_trips_count_similar = fields.Integer()
    process_start_date = fields.DateTime()
    process_end_date_list = fields.DateTime()
    process_end_date = fields.DateTime()

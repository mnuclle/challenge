from app.db import db, BaseModelMixin

from datetime import datetime

from shapely import geometry
from sqlalchemy import and_

from shapely.geometry import Point
from app.support.point import Point as pt


class Trip(db.Model, BaseModelMixin):
    __tablename__ = 'trips'
    trip_id = db.Column(db.Integer, primary_key=True)
    origin_latitude = db.Column(db.String(250))
    origin_longitude = db.Column(db.String(250))
    destination_latitude = db.Column(db.String(250))
    destination_longitude = db.Column(db.String(250))
    date = db.Column(db.DateTime)
    datasource_id = db.Column(db.Integer, db.ForeignKey('datasources.datasource_id'))
    region_id = db.Column(db.Integer, db.ForeignKey('regions.region_id'))

    def __init__(self, trip_id, origin_latitude, origin_longitude, destination_latitude, destination_longitude, date,
                 datasource_id, region_id):
        self.trip_id = trip_id
        self.origin_latitude = origin_latitude
        self.origin_longitude = origin_longitude
        self.destination_latitude = destination_latitude
        self.destination_longitude = destination_longitude
        self.date = date
        self.datasource_id = datasource_id
        self.region_id = region_id

    def __repr__(self):
        return f'Trip({self.trip_id})'

    def __str__(self):
        return f'{self.trip_id}'

    @classmethod
    def find_trips_in_week(cls, region_name, start_date, end_date):
        region_id = Region.query.filter_by(name=region_name).first().region_id
        trips = Trip.query.filter(Trip.region_id == region_id).filter(
            and_(Trip.date >= start_date, Trip.date <= end_date)).all()
        return trips

    @classmethod
    def get_all(cls):
        return Trip.query.all()

    def is_inside(self, polygon_points):
        origin_point = Point(float(self.origin_latitude), float(self.origin_longitude))
        destination_point = Point(float(self.destination_latitude), float(self.destination_longitude))

        point_list = []
        for point in polygon_points:
            new_pt = pt(point)
            new_point = Point(float(new_pt.latitude), float(new_pt.longitude))
            point_list.append(new_point)

        polygon = geometry.Polygon([[p.y, p.x] for p in point_list])
        return polygon.contains(origin_point) & polygon.contains(destination_point)

    @classmethod
    def bulk_save(cls, trips):
        db.session.bulk_save_objects(trips)
        db.session.commit()


class SimilarTrips(db.Model, BaseModelMixin):
    __tablename__ = 'similar_trips'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.trip_id'))
    similar_trip_id = db.Column(db.Integer, db.ForeignKey('trips.trip_id'))

    def __init__(self,trip_id, similar_trip_id):
        self.trip_id = trip_id
        self.similar_trip_id = similar_trip_id

    def __repr__(self):
        return f'SimilarTrips({self.id})'

    def __str__(self):
        return f'{self.id}'

    @classmethod
    def bulk_save(cls, similar_trips):
        db.session.bulk_save_objects(similar_trips)
        db.session.commit()

class Region(db.Model, BaseModelMixin):
    __tablename__ = 'regions'
    region_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    trips = db.relationship('Trip', backref='trips')

    def __init__(self, name, trips=[]):
        self.name = name
        self.trips = trips

    def __repr__(self):
        return f'Region({self.region_id})'

    def __str__(self):
        return f'{self.region_id}'


    @classmethod
    def save_all(cls,regions):
        db.session.add_all(regions)
        db.session.commit()

    @classmethod
    def find_by_name(cls, name):
        region = Region.query.filter_by(name=name).first()
        return region.region_id

    @classmethod
    def find_trips(cls, name):
        trips = Region.query.filter_by(name=name).first().trips
        return trips


class Datasource(db.Model, BaseModelMixin):
    __tablename__ = 'datasources'
    datasource_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    datasource_trips = db.relationship('Trip', backref='datasource_trips')

    def __init__(self, name, trips=[]):
        self.name = name
        self.trips = trips

    def __repr__(self):
        return f'Datasource({self.datasource_id})'

    def __str__(self):
        return f'{self.datasource_id}'

    @classmethod
    def save_all(cls, datasources):
        db.session.add_all(datasources)
        db.session.commit()

    @classmethod
    def find_by_name(cls, name):
        datasource = Datasource.query.filter_by(name=name).first()
        return datasource.datasource_id


class CsvFile(db.Model, BaseModelMixin):
    __tablename__ = 'files'
    file_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    trip_count = db.Column(db.Integer)
    trip_similar_keys = db.Column(db.Integer)
    processed_trips_count_list = db.Column(db.Integer)
    processed_trips_count_similar = db.Column(db.Integer)
    process_start_date = db.Column(db.DateTime)
    process_end_date_list = db.Column(db.DateTime)
    process_end_date = db.Column(db.DateTime)

    def __init__(self, name, trip_count, trip_similar_keys, processed_trips_count_list, processed_trips_count_similar,
                 process_start_date, process_end_date_list, process_end_date):
        self.name = name
        self.trip_count = trip_count
        self.trip_similar_keys = trip_similar_keys
        self.processed_trips_count_list = processed_trips_count_list
        self.processed_trips_count_similar = processed_trips_count_similar
        self.process_start_date = process_start_date
        self.process_end_date_list = process_end_date_list
        self.process_end_date = process_end_date

    def __repr__(self):
        return f'CsvFile({self.file_id})'

    def __str__(self):
        return f'{self.file_id}'


    def save(self):
        db.session.add(self)
        db.session.commit()
        return self.file_id

    @classmethod
    def save_proccess_status_list(cls, count, file_id, count_keys):
        file = CsvFile.query.get(file_id)

        if file.trip_count == count:
            file.processed_trips_count_list = count
            file.process_end_date_list = datetime.today()
            file.trip_similar_keys = count_keys
        else:
            file.processed_trips_count_list = count
        db.session.commit()

    @classmethod
    def save_proccess_status_similar(cls, count, file_id):
        file = CsvFile.query.get(file_id)

        if file.trip_similar_keys == count:
            file.processed_trips_count_similar = count
            file.process_end_date = datetime.today()
        else:
            file.processed_trips_count_similar = count
        db.session.commit()

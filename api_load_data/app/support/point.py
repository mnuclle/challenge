class Point:
    def __init__(self, value):
        self._longitude = (value[value.find('(')+1:value.find(' ', 7)]).strip()
        self._latitude = value[value.find(' ', 7):value.find(')')]

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    def __str__(self):
        return f'Latitude: {self._latitude} and longitude: {self._longitude}'
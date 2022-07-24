#!/usr/bin/env python3

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

import settings

class influxdb_logger:
    def __init__(self, measurement):
        url = settings.url
        token = settings.token
        self.org = settings.org
        self.bucket = settings.bucket
        self.measurement = measurement

        client = InfluxDBClient(url=url, token=token, org=self.org)
        self.write_api = client.write_api(write_options=SYNCHRONOUS)

    def write(self, time, fields):
        point = Point(self.measurement) \
            .time(int(time * 1000), WritePrecision.MS)
        for name, value in fields:
            point = point.field(name, value)
        self.write_api.write(self.bucket, self.org, point)

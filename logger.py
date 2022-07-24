#!/usr/bin/env python3

import queue
import threading

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

import settings

class InfluxdbLogger:
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


def influxdb_main(measurement, influxdb_queue):
    """Thread to communicate with the InfluxDB server.

    This is done in a separate thread to avoid long pauses in the
    measurement thread in case writing the data takes some time.
    """

    influxdb_logger = InfluxdbLogger(measurement)
    while True:
        time, fields = influxdb_queue.get()
        influxdb_logger.write(time, fields)
        influxdb_queue.task_done()


class Logger:
    def __init__(self, measurement):
        self.influxdb_queue = queue.Queue(maxsize=100)
        self.influxdb_thread = threading.Thread(
            target = influxdb_main,
            args = (measurement, self.influxdb_queue),
        )
        self.influxdb_thread.start()


    def write(self, time, fields):
        # Never block here to make sure the measurement code keeps running.
        # If a queue gets full for some reason, discard the data.
        try:
            self.influxdb_queue.put((time, fields), block=False)
        except queue.Full:
            pass

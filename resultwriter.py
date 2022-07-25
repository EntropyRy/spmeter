#!/usr/bin/env python3
"""Measurement result writer.

This module contains code to store measurement results.
Results can be stored in multiple different destinations.

I/O is done in a separate threads to avoid long pauses
in the measurement thread in case the I/O takes some time.
If writing to some destination fails, other writers can still keep working.
For example, if connection to a database is lost, results may be still
written to a CSV file.
"""

import queue
import threading

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

import settings

class InfluxdbWriter:
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

# TODO: move CSV writing here to a writer class


def writer_main(measurement, writer_class, writer_queue):
    """Main function of a thread that stores the data somewhere.
    Where the data is stored depends on the writer class given.
    """

    writer = writer_class(measurement)
    while True:
        time, fields = writer_queue.get()
        writer.write(time, fields)
        writer_queue.task_done()


class Writer:
    def __init__(self, measurement, enable_influxdb=True):
        self.queues = list()

        if enable_influxdb:
            self.start_writer(measurement, InfluxdbWriter)

    def start_writer(self, measurement, writer_class):
        """Start a writer thread and create a queue
        to communicate with the thread.
        """
        q = queue.Queue(maxsize=100)
        self.influxdb_thread = threading.Thread(
            target = writer_main,
            args = (measurement, writer_class, q),
        )
        self.influxdb_thread.start()
        self.queues.append(q)

    def write(self, time, fields):
        """Store a measurement record.
        """
        # Send the data to each writer thread through a queue.
        # Never block here to make sure the measurement code keeps running.
        # If a queue gets full for some reason, discard the data.
        for q in self.queues:
            try:
                q.put((time, fields), block=False)
            except queue.Full:
                pass
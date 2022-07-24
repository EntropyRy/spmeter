# Sound pressure meter

This is a simple sound level logger running on Linux.

## Setting it up

Modify `measure.sh` if the name of your soundcard is different.

Write settings for InfluxDB connection in `settings.py`.

The repository should be placed in your home directory at `~/spmeter`
for the service file to work.
To install the service, run `install_service.sh`.

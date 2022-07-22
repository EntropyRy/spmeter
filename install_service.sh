#!/bin/sh
SERVICE_DIR="${HOME}/.config/systemd/user"
set -e -x
mkdir -p "${SERVICE_DIR}"
cp spmeter.service "${SERVICE_DIR}"
systemctl --user daemon-reload
systemctl --user enable spmeter.service
systemctl --user start default.target
set +x
echo
echo "Service installed."
echo "To make it start automatically, you might have to run as root:"
echo "sudo loginctl enable-linger ${USER}"

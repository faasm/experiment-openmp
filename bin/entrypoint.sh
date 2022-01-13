#!/bin/bash
set -e

# Start hoststats
nohup hoststats start > /var/log/hoststats.log 2>&1 &

sleep infinity

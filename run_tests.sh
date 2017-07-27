#!/bin/sh

python -m j2pbs.tests.test_job > /dev/null
python -m j2pbs.tests.test_graph > /dev/null

#!/bin/bash
set -ex
toolforge build start https://gitlab.wikimedia.org/toolforge-repos/link-dispenser
cd link-dispenser
toolforge webservice restart
cd link-dispenser
toolforge jobs delete crawljob
toolforge jobs load jobs.yaml
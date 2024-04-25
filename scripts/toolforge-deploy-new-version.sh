#!/bin/bash
set -ex
toolforge build start https://gitlab.wikimedia.org/toolforge-repos/link-dispenser
cd link-dispenser
toolforge webservice restart
toolforge jobs delete crawljob
toolforge jobs load jobs.yaml
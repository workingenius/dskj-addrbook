#!/bin/bash
export PATH="/home/ytjx/miniconda2/bin/:$PATH"
. activate dskj-addrbook
which python
cd /home/ytjx/service
uwsgi /home/ytjx/service/uwsgi.ini

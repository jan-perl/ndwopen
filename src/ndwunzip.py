# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
#basic unzip data mailed from  https://dexter.ndw.nu/opendata
#put data into ..data/zipin; this workbook unzips
# -

import rdwbas

import re
import io
import time
import glob
import os

os.system('cd ../data/zipin; for t in *.zip ; do unzip $t; mv *.xlsx ../$(echo $t| sed -e "s+.xlsx.zip$++" -e "s+.zip$++").xlsx ; done')

os.system('cp -p -u ../../ODINmod01/intermediate/gem1*_GM*.pkl ../data')

os.system('ls -ltrac ../data')



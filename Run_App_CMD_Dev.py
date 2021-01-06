# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 09:38:45 2020

@author: aa63
"""

import sys
from streamlit import cli as stcli

if __name__ == '__main__':
    sys.argv = ["streamlit", "run", "https://raw.githubusercontent.com/abirashedanna/streamlit/master/IMM_PRJ_ST.py"]
    sys.exit(stcli.main())


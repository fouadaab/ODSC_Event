#!/usr/bin/env python
# coding: utf-8

from selenium_ODSC import connect

driver = connect(url="https://live.odsc.com/#topics-tab",
                 #option='-headless'
                )

driver.login2menu()

driver.get_replays()

driver.close()

driver.download2drive(file_dl='dl_complete.dat')

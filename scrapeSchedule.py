#!/usr/bin/python3.9
import time
import schedule
from webscrape import WebScraper

ws = WebScraper()
schedule.every().day.at("01:00").do(ws.scrape)

while True:
    schedule.run_pending()
    time.sleep(36000) # wait one hour


# Schedule the script to run once a day at midnight
while True:
    # Get the current time
    now = time.localtime()

    # If it's midnight, run the script and wait until the next day
    if now.tm_hour == 1 and now.tm_min == 0:

        # Run the script once at startup
        ws.scrape()
        ws.convertAndMerge()

        time.sleep(86400)
    # Otherwise, wait 10 minutes and check again
    else:
        time.sleep(600)

#chmod +x /path/to/schedule.py to enable execution

#sudo nano /etc/systemd/system/schedule.service ---- this will allow the code to run on boot


""" schedule.service ==
[Unit]
Description=Daily Scheduler

[Service]
Type=simple
ExecStart=/path/to/schedule.py

[Install]
WantedBy=multi-user.target
"""
#run
# sudo systemctl daemon-reload

#then run to enable service on startup
#sudo systemctl enable schedule.service

#optional start now
#sudo systemctl start schedule.service


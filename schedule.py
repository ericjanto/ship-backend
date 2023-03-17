import time

# Run the script once at startup
exec(open('/path/to/my_script.py').read())

# Schedule the script to run once a day at midnight
while True:
    # Get the current time
    now = time.localtime()

    # If it's midnight, run the script and wait until the next day
    if now.tm_hour == 12 and now.tm_min == 0:
        exec(open('./webscrape.py').read())
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


from crontab import CronTab
from amt_util import *
from dateutil import tz


cron = CronTab(user='pi')

for job in cron:
    print(job)

now = datetime.today()

for i in range(7):
    starttime, endtime = getsuntimes(-35.264, 149.084, now.replace(tzinfo=tz.tzlocal()))

    print("Sunset: " + str(starttime) + " Sunrise: " + str(endtime))
    starttime += timedelta(minutes = 60)
    endtime += timedelta(minutes = -120)

    job = cron.new(command = 'python3 /home/pi/amt_timelapse.py', comment = 'CronTest.py')
    job.hour.on(starttime.hour)
    job.minute.on(starttime.minute)
    job.day.on(starttime.day)
    job.month.on(starttime.month)

    print(job)

    now += timedelta(hours = 24)
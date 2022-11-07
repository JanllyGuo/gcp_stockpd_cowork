from crontab import CronTab

# stockpd : your linux account
my_cron = CronTab(user='stockpd')

job = my_cron.new(command='/usr/bin/python3 /home/stockpd/get-stock-data-image-upload-storage/upload_data_image.py', comment='uploadStorage')

#job.minute.every(5)
job.setall('30 14 * * *')

my_cron.write()


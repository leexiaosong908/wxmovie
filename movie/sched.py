import schedule
import time
import threading


def job():
    with open('sched1.log','a') as f:
        print('working',file=f)
def job_task():
    threading.Thread(target=job).start()

def job2():
    with open('sched2.log','a') as f:
        print('job2',file=f)
def job2_task():
    threading.Thread(target=job2).start()



schedule.every(2).seconds.do(job_task)
schedule.every(5).seconds.do(job2_task)
schedule.every().day.at("20:59").do(job2_task)

while True:
    schedule.run_pending()
    time.sleep(1)

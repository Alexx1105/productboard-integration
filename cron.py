import schedule
import time
import threading
from typing import Callable
from functools import wraps
from datetime import datetime


class CronScheduler:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):         ##single source of truth, make sure no new instances are generated
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
            
    def __init__(self):              ##init cron object, run only once 
        if not self._initialized:
            self.scheduler_thread = None
            self.is_running = False
            self._initialized = True
                    
    def schedulingLoop(self):
            self.is_running = True
            while self.is_running:
             schedule.run_pending()
             time.sleep(300)  ## check every 5 minutes, maybe change later
                        
    def startScheduler(self):           ##start the scheduler in background daemon thread
        if not self.scheduler_thread:
         self.scheduler_thread = threading.Thread(target = self.schedulingLoop, daemon = True) ##run on loop
        self.scheduler_thread.start()
                        
    def stopScheduler(self):
        self.is_running = False
        if self.scheduler_thread:
         self.scheduler_thread.join()   ##exit loop
         self.scheduler_thread = None         
         schedule.clear()              ##clear running scheduler
                            
    def timeIntervals(self, func: Callable, interval: int, unit: str):
            match unit:
              case "seconds":
                schedule.every(interval).seconds.do(func)
              case "minutes":
                schedule.every(interval).seconds.do(func)
              case "hours":
                schedule.every(interval).seconds.do(func)
              case "days":    
                schedule.every(interval).seconds.do(func)
              case _ :
                raise ValueError("time interval scheduling failure")
     
    @staticmethod                          
    def wrapFunc(interval: int, unit: str = "minutes"):    ## call functions, make func into scheduled lambda
        def decorator(func):
            @wraps(func)
                                
            def wrapper(*args, **kwargs):
                cron = CronScheduler()
                wrappedFunc = lambda: func(datetime.now().isoformat())   
                cron.timeIntervals(wrappedFunc, interval, unit)
                cron.startScheduler()
                return func(datetime.now().isoformat())
            return wrapper
        return decorator
    
@CronScheduler.wrapFunc(interval = 5, unit = "seconds")   ##cron test
def cronTick(timestamp: str) -> int: 
  print(f"timestamp tick: {timestamp}")
  return timestamp

def main():
 sch = CronScheduler()
 try:
  cronTick()
  while True:
     sch.startScheduler()
     time.sleep(1)
 except:
      print("stopping the scheduling function works")
      sch.stopScheduler()
 
 
if __name__ == "__main__":
    main()

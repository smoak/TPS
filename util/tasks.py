import threading, time

class PeriodicExecutor(threading.Thread):
    def __init__(self,sleep,func,params):
        """ execute func(params) every 'sleep' seconds """
        self.func = func
        self.params = params
        self.sleep = sleep
        threading.Thread.__init__(self,name = "PeriodicExecutor")
        self.setDaemon(1)
    def run(self):
        while 1:
            time.sleep(self.sleep)
            apply(self.func,self.params)

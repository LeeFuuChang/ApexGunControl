import traceback
import threading
import logging
import time
logger = logging.getLogger()





class TaskThread(threading.Thread):
    running = {}
    def __init__(self, target, interval=0, delay=0, tries=5, fargs=(), onFinished=lambda:None):
        super(self.__class__, self).__init__(target=self.wrappedFunction, daemon=True)
        self.target = target
        self.threadName = self.target.__name__
        self.event = threading.Event()
        self.interval = interval
        self.delay = delay
        self.tries = tries
        self.fargs = fargs
        self.onFinished = onFinished

    def finish(self):
        if(self.threadName in self.running): 
            del self.running[self.threadName]
        if(not self.event.is_set()):
            self.event.set()
            self.onFinished()

    def wrappedFunction(self):
        passed = False
        time.sleep(self.delay)
        while(not self.event.is_set() and not passed and self.tries != 0):
            try:
                passed = self.target(*self.fargs)
            except Exception as e:
                logger.error(traceback.format_exc())
            finally:
                self.tries -= 1
                time.sleep(self.interval)
        else: self.finish()

    def start(self):
        if(self.threadName not in self.running):
            self.running[self.threadName] = self
            super().start()
        return self.running[self.threadName]





class SteppedTaskThread(threading.Thread):
    running = {}
    def __init__(self, targets, delay=0, tries=5, fargs=(), onFinished=lambda:None):
        super(self.__class__, self).__init__(target=self.wrappedFunction, daemon=True)
        self.targets = targets
        self.threadName = "+".join([t.__name__ for t in self.targets])
        self.targetIndex = 0
        self.event = threading.Event()
        self.delay = delay
        self.tries = tries
        self.fargs = fargs
        self.onFinished = onFinished

    def finish(self):
        if(self.threadName in self.running): 
            del self.running[self.threadName]
        if(not self.event.is_set()):
            self.event.set()
            self.onFinished()

    def wrappedFunction(self):
        passed = False
        time.sleep(self.delay)
        while(not self.event.is_set() and self.targetIndex<len(self.targets) and self.tries != 0):
            try:
                passed = self.targets[self.targetIndex](*self.fargs)
            except Exception as e:
                logger.error(traceback.format_exc())
            finally:
                self.targetIndex += passed
                self.tries -= 1
        else: self.finish()

    def start(self):
        if(self.threadName not in self.running):
            self.running[self.threadName] = self
            super().start()
        return self.running[self.threadName]





class TimedTaskThread(threading.Thread):
    running = {}
    def __init__(self, target, interval=1, delay=0, repeat=1, tries=5, fargs=(), onFinished=lambda:None):
        super(self.__class__, self).__init__(target=self.wrappedFunction, daemon=True)
        self.target = target
        self.threadName = self.target.__name__
        self.event = threading.Event()
        self.threads = {}
        self.interval = interval
        self.delay = delay
        self.repeat = repeat
        self.tries = tries
        self.fargs = fargs
        self.onFinished = onFinished

    def finish(self):
        if(self.threadName in self.running): 
            del self.running[self.threadName]
        if(not self.event.is_set()):
            self.event.set()
            self.onFinished()

    def wrappedOnce(self, tid):
        passed = False
        try: 
            if(not self.event.is_set()):
                passed = self.target(*self.fargs)
        except Exception as e:
            logger.error(traceback.format_exc())
        finally: 
            self.repeat -= passed
            del self.threads[tid]
            if(not self.repeat): self.finish()

    def wrappedFunction(self):
        time.sleep(self.delay)
        while(not self.event.is_set() and self.repeat != 0 and self.tries != 0):
            tid = time.time()
            thread = threading.Thread(target=self.wrappedOnce, daemon=True, args=(tid, ))
            thread.start()
            self.threads[tid] = thread
            self.tries -= 1
            time.sleep(self.interval)
        else: self.finish()

    def start(self):
        if(self.threadName not in self.running):
            self.running[self.threadName] = self
            super().start()
        return self.running[self.threadName]





class OnceThread(threading.Thread):
    running = {}
    def __init__(self, target, delay=0, fargs=(), onFinished=lambda:None):
        super(self.__class__, self).__init__(target=self.wrappedFunction, daemon=True)
        self.target = target
        self.threadName = self.target.__name__
        self.delay = delay
        self.fargs = fargs
        self.onFinished = onFinished

    def wrappedFunction(self):
        time.sleep(self.delay)
        try:
            self.target(*self.fargs)
        except Exception as e:
            logger.error(traceback.format_exc())
        finally:
            if(self.threadName in self.running): 
                del self.running[self.threadName]
            self.onFinished()

    def start(self):
        if(self.threadName not in self.running):
            self.running[self.threadName] = self
            super().start()
        return self.running[self.threadName]





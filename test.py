from threading import Thread, Event

class MyThread(Thread):
	def __init__(self, event):
		Thread.__init__(self)
		self.stopped = event

	def run(self):
		while not self.stopped.wait(1):
			print("hello world")

my_event = Event()
thread = MyThread(my_event)
thread.start()
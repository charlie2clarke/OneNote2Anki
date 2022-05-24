import logging
from queue import Queue
from threading import Thread

import events


class AuthoriseWorker(Thread):
    def __init__(self, queue: Queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self) -> None:
        while True:
            event = self.queue.get()

            if event.type == "authorise":
                events.AuthorisationSuccess = event
                try:
                    events.AuthorisationSuccess.handler()
                except Exception as e:
                    logging.error(e)
            elif event.type == "token":
                events.TokenSuccess = event
                self.queue.task_done()
                events.TokenSuccess.handler()

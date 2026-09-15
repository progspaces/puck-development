from threading import Thread
from typing import Self
from queue import Queue

class Actor(Thread):
    def __init__(self, target):
        super().__init__(target=target, args=(self,))
        self.mailbox: Queue = Queue()

    def send(self:Self, message):
        """
        Sends message to the actor in actor.send()

        Args:
            self (Self): actor
            message (_type_): any object
        """
        self.mailbox.put(message)

    def recieve(self): 
        return self.mailbox.get()

    def end(self):
        self.send({"type": "kill"})
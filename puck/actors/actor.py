import itertools
from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Thread, local
from typing import Any

from .id import ActorID
from .mailbox import Mailbox

# an actor function is a function that can have any args and returns None
ActorFunction = Callable[..., None]


@dataclass
class Actor:
    """Holds all the information about a specific actor.

    For convinience there is also a reference to the ActorSystem that is
    running the actor.
    """

    id: ActorID
    system: "ActorSystem"
    mailbox: Mailbox = field(default_factory=Mailbox)


# a thread local object to hold each threads instance of the Actor class
# See https://docs.python.org/3/library/threading.html#thread-local-data.
thread_context = local()


def set_local_actor(actor: Actor):
    thread_context.actor = actor


class ActorSystem:
    """A container for the actors."""

    def __init__(self) -> None:
        self.next_id = itertools.count(1)
        self.actors: dict[ActorID, Actor] = {}

    def next_actor(self):
        id = ActorID(next(self.next_id))
        actor = Actor(id=id, system=self)
        self.actors[id] = actor
        return actor

    def run(self, target: ActorFunction, *args: Any, **kwargs: Any) -> ActorID:
        """Creates a new actor in the system based on the function that is passed in.

        Args:
            target (ActorFunction): The function to run as the actor.

        Returns:
            ActorID: The actor id object, used to send messages to the actor.
        """

        actor = self.next_actor()

        def run_actor():
            set_local_actor(actor)
            try:
                target(*args, **kwargs)
            finally:
                del self.actors[actor.id]
                del thread_context.actor

        # initialise the thread to target the run_actor function
        thread = Thread(target=run_actor)

        try:
            # start the thread
            thread.start()
        except Exception:
            # if it fails remove it for the actors list
            del self.actors[actor.id]
            raise
        return actor.id


def spawn(target: ActorFunction, *args: Any, **kwargs: Any) -> ActorID:
    """Spawn a new actor.

    Args:
        target (ActorFunction): The function to run in the actor.

    Returns:
        ActorID: The id of the new actor.
    """
    return thread_context.actor.system.run(target, *args, **kwargs)


def send(id: ActorID, message: Any) -> None:
    """Send an actor a message.

    Messages can be of any type. Convention is strings or tuples.
    String if the messages have no arguments.
    Tuples if they have arguments.

    Args:
        id (ActorID): The id of the target actor.
        message (Any): The message to send.
    """
    target = thread_context.actor.system.actors[id]
    target.mailbox.put(message)


def receive(
    block: bool = True, timeout: float | None = None
) -> Any:  # what about a optional type?
    """Recieve the next message in the mailbox.

    Blocks and waits until there is a message in the mailbox then gets it.

    Returns:
        Any: The next message in the mailbox.
    """
    mailbox = thread_context.actor.mailbox
    return mailbox.get(block, timeout)


def me() -> ActorID:
    """Get the id of the current actor.

    Equivalent to self in Erlang.

    Returns:
        ActorID: The id of the current actor.
    """
    return thread_context.actor.id

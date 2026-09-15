from dataclasses import dataclass


@dataclass(frozen=True)
class ActorID:
    """Identifies an actor in the system.
    Equivilent to an Erlang PID.

    If we move to a distributed system, this can be exteneded to a more
    complex address. Also we could us it as an adapter to fake method style
    sends. E.g. my_actor.send(()) rather then send(my_actor, ()).
    """

    identifier: int

    def __str__(self) -> str:
        return str(self.identifier)

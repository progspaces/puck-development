from typing import Any, Callable, Tuple

from .actor import ActorFunction, ActorSystem, set_local_actor
from .id import ActorID


def run(
    target: ActorFunction, *args: Any, **kwargs: Any
) -> Tuple[ActorID, ActorSystem]:
    """Run starts the target function as an actor in a new ActorSystem.

    This helper abstracts a common pattern used when programs are started.
    It let's you just do something like:

    if __name__ == "__main__":
        run(main)

    where main is the function for an actor.

    Args:
        target (ActorFunction): The function to run in the actor.

    Returns:
        Tuple[ActorID, ActorSystem]: The id of the new actor and the system.
    """
    system = ActorSystem()
    id = system.run(target, *args, **kwargs)
    return id, system


# should this function be in the public API?
def setup_main_thread() -> None:
    system = ActorSystem()
    actor = system.next_actor()
    set_local_actor(actor)

    # doesn't do the teardown but is it needed?


def run_main(func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
    """Create an actor for the main thread and then run the passesd function.

    This helper abstracts a common pattern used when programs are started.
    It let's you just do something like:

    if __name__ == "__main__":
        start(main)

    The start is like run but

    Args:
        func (_type_): _description_
    """
    setup_main_thread()
    func(*args, **kwargs)

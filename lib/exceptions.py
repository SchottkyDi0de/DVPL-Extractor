import traceback
from typing import Any, TYPE_CHECKING
from collections.abc import Callable

if TYPE_CHECKING:
    from ui.main import MasterFrame

def wrap_exceptions(frame_pos: int, ignore_exceptions: tuple) -> Callable[..., Callable[..., Any]]:
    """
    A decorator that wraps a function to catch and handle exceptions.

    Args:
            frame_name (Literal['frame', 'master_frame', 'log_frame']): The name of the frame to use for logging.

    Returns:
            Callable[..., Callable[..., None]]: A decorator that takes a function as an argument and returns a new function that wraps the original function.
    """
    def decorator(func) -> Callable[..., None]:
        def wrapper(*args, **kwargs) -> None:
            try:
                func(*args, **kwargs)
            except Exception as e:
                try:
                    frame = args[frame_pos]
                except (KeyError, ValueError) as e:
                    raise e
                else:
                    if frame is None:
                        raise e
                    elif hasattr(frame, 'log_frame'):
                        frame: 'MasterFrame'
                        if e in ignore_exceptions:
                            frame.log_frame.add_log(traceback.format_exc(), prefix="[stderr]: ")
                            return
                        
                        frame.log_frame.add_log(traceback.format_exc(), prefix="[stderr]: ")
                        frame.set_state_on_error(e)
                    else:
                        if e in ignore_exceptions:
                            return
                        else:
                            raise e

        return wrapper

    return decorator

import contextvars

current_engine = contextvars.ContextVar("current_engine")


def get_current_engine():
    try:
        return current_engine.get()
    except LookupError as e:
        raise Exception("No engine set. Did you enter the context?") from e


def set_current_engine(engine):
    current_engine.set(engine)

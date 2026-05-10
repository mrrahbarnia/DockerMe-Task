from dataclasses import asdict

EVENT_REGISTRY: dict[str, type["Event"]] = {}


class Event:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # auto register every event
        EVENT_REGISTRY[cls.__name__] = cls

    def to_dict(self) -> dict:
        return asdict(self)  # type: ignore

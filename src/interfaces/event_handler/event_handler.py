from src.application.events.event import Event


class EventHandler:
    def handle(self, event: Event): ...

<!-- NT v2 compatibility note: legacy: v1 Python example retained as migration/reference-only; not a production default. -->
# Example: Self-Communication Using Message Bus

NT v2 compatibility note: legacy: this v1 Python example is migration/reference-only; not a production default.

A practical demonstration of using NautilusTrader's message bus for self-communication within a strategy.
The example implements a "10th bar notification system" where the strategy:

1. Creates a custom event (using Python's dataclass) to represent the 10th bar occurrence.
2. Publishes this event to the message bus when the 10th bar arrives.
3. Subscribes to and handles these events within the same strategy.

**Key learning points**:

- Creating custom events with the message bus.
- Implementing publish/subscribe pattern for self-communication.
- Using events for condition-based notifications.
- Handling state changes through message bus events.

This pattern provides a clean, event-driven approach to handle conditional notifications
and state changes within your trading strategies.

**Note:**
While this example shows both publisher and subscriber roles within a single strategy, in practice these roles
can be distributed - any component can be a publisher and any other component can be a subscriber of events.

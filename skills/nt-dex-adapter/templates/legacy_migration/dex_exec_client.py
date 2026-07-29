# TEMPLATE_CLASSIFICATION: legacy executable; migration/reference-only; not a production default
"""
DEX Adapter Template: Execution Client

Handles wallet-signed on-chain order submission, cancellation, and account state.

Phases 4–5 of the 7-phase DEX adapter implementation sequence.

Key differences from CeFi execution clients:
- No API keys — uses wallet private key + transaction signing
- Order flow: build tx → sign → broadcast → wait for receipt → emit events
- Fill price is actual output amount from tx receipt (not exchange-reported)
- Gas cost is included as commission in order fill events
- Account state is on-chain wallet balance (queried after each tx)

Replace 'MyDEX' with your actual DEX name throughout.
"""

import sys
from pathlib import Path

from nautilus_trader.cache.cache import Cache
from nautilus_trader.common.component import LiveClock, MessageBus
from nautilus_trader.live.execution_client import LiveExecutionClient
from nautilus_trader.model.enums import (
    AccountType,
    OmsType,
)
from nautilus_trader.model.identifiers import (
    AccountId,
    ClientId,
    ClientOrderId,
    InstrumentId,
    VenueOrderId,
    Venue,
)
from nautilus_trader.model.orders import Order
from nautilus_trader.execution.reports import OrderStatusReport

_TEMPLATE_DIR = Path(__file__).resolve().parent
if str(_TEMPLATE_DIR) not in sys.path:
    sys.path.append(str(_TEMPLATE_DIR))

# The templates must work both as package imports and as standalone files loaded
# by compliance tests or copied into a project. The sys.path bridge above keeps
# fallback sibling imports available in the latter mode.
try:
    from .dex_config import MyDEXExecClientConfig  # noqa: E402
    from .dex_instrument_provider import MyDEXInstrumentProvider  # noqa: E402
except ImportError:
    from dex_config import MyDEXExecClientConfig  # noqa: E402
    from dex_instrument_provider import MyDEXInstrumentProvider  # noqa: E402


class MyDEXExecutionClient(LiveExecutionClient):
    """
    Execution client for MyDEX.

    Submits orders as wallet-signed on-chain transactions and maps
    transaction outcomes back to Nautilus order lifecycle events.

    Parameters
    ----------
    client_id : ClientId
        The client identifier (e.g. ClientId("MYDEX")).
    venue : Venue
        The venue (e.g. Venue("MYDEX")).
    account_id : AccountId
        The account identifier.
    msgbus : MessageBus
        The Nautilus message bus.
    cache : Cache
        The Nautilus cache.
    clock : LiveClock
        The Nautilus clock.
    instrument_provider : MyDEXInstrumentProvider
        Loaded instrument definitions.
    config : MyDEXExecClientConfig
        Client configuration (includes private key as SecretStr).
    """

    def __init__(
        self,
        client_id: ClientId,
        venue: Venue,
        account_id: AccountId,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        instrument_provider: MyDEXInstrumentProvider,
        config: MyDEXExecClientConfig,
    ) -> None:
        super().__init__(
            client_id=client_id,
            venue=venue,
            oms_type=OmsType.NETTING,
            account_type=AccountType.CASH,
            base_currency=None,
            msgbus=msgbus,
            cache=cache,
            clock=clock,
        )
        self._instrument_provider = instrument_provider
        self._config = config
        self._account_id = account_id

        # DEX execution state
        self._pending_txs: dict[ClientOrderId, str] = {}  # order_id → tx_hash

        # Private key is accessed via SecretStr.get_secret_value() in the Rust client
        # self._signing_client = MyDEXSigningClient(
        #     rpc_url=config.rpc_url,
        #     private_key=config.private_key.get_secret_value(),
        #     chain_id=config.chain_id,
        # )

    # ─── LIFECYCLE ─────────────────────────────────────────────────────────────

    async def _connect(self) -> None:
        """
        Connect to the DEX execution layer.

        1. Verifies RPC connectivity
        2. Loads initial account state from on-chain wallet
        3. Instruments must already be loaded by the data client
        """
        self.log.info(
            f"Connecting to MyDEX execution (wallet: {self._config.wallet_address})"
        )

        # Fetch and report initial account state
        await self._update_account_state()

    async def _disconnect(self) -> None:
        """Disconnect gracefully — no open orders to cancel on AMM."""
        self.log.info("Disconnecting from MyDEX execution")

    # ─── ORDER COMMANDS ────────────────────────────────────────────────────────

    async def _submit_order(self, command) -> None:
        """
        Submit an order as a signed on-chain transaction.

        Flow:
        1. Build and sign via the venue client
        2. Broadcast the transaction
        3. Validate the returned transaction hash
        4. Emit submission only after successful broadcast
        5. Resolve lifecycle only from authoritative receipt data

        Parameters
        ----------
        order : Order
            The Nautilus order to submit.
        """
        raise NotImplementedError(
            "DEX transaction building, signing, and broadcast must be implemented before submission",
        )

    async def _cancel_order(self, command) -> None:
        """
        Cancel a pending order.

        Note: Most AMM DEX swaps cannot be cancelled once submitted to the mempool.
        Implement speed-bump cancellation (replace-by-fee) or raise NotImplementedError
        with a clear explanation.
        """
        raise NotImplementedError(
            "DEX cancellation requires an authoritative venue cancel or replace-by-fee transaction",
        )

    async def _cancel_all_orders(self, command) -> None:
        raise NotImplementedError(
            "DEX bulk cancellation requires an authoritative venue cancel transaction",
        )

    async def _modify_order(self, command) -> None:
        """Modify is not supported on most DEX venues."""
        self.log.warning(f"Order modification not supported on DEX: {command.client_order_id}")

    async def _query_order(self, command) -> None:
        """Query order status by checking on-chain tx receipt."""
        client_order_id = command.client_order_id
        tx_hash = self._pending_txs.get(client_order_id)
        if tx_hash is None:
            self.log.warning(f"No tx hash found for order: {client_order_id}")
            return
        # receipt = await self._signing_client.get_receipt(tx_hash)
        # self._handle_receipt(client_order_id, receipt)

    # ─── ACCOUNT STATE ─────────────────────────────────────────────────────────

    async def _update_account_state(self) -> None:
        """
        Fetch on-chain wallet balances and emit AccountState.

        Must be called:
        - On connect
        - After every trade execution
        - Periodically to stay in sync (use a timer in the actor)
        """
        raise NotImplementedError(
            "DEX account state requires a successful authoritative on-chain balance query",
        )

    # ─── RECONCILIATION ────────────────────────────────────────────────────────

    async def generate_order_status_report(
        self,
        instrument_id: InstrumentId,
        client_order_id: ClientOrderId | None = None,
        venue_order_id: VenueOrderId | None = None,
    ) -> OrderStatusReport | None:
        """
        Generate an order status report for reconciliation.

        Reconciliation follows TC-E84–87: only a successful authoritative venue
        query can establish order, fill, position, or zero-result state.
        """
        raise NotImplementedError(
            "DEX order reconciliation requires an authoritative venue transaction query",
        )

    async def generate_order_status_reports(self, *args, **kwargs):
        """Generate all available order status reports for reconciliation."""
        raise NotImplementedError(
            "DEX order reconciliation requires a successful authoritative venue query",
        )

    async def generate_fill_reports(self, *args, **kwargs):
        """Generate fill reports for reconciliation."""
        raise NotImplementedError(
            "DEX fill reconciliation requires parsed authoritative on-chain logs",
        )

    async def generate_position_status_reports(self, *args, **kwargs):
        """Generate position status reports for reconciliation."""
        raise NotImplementedError(
            "DEX position reconciliation requires a successful authoritative venue query",
        )

    async def generate_mass_status(self, *args, **kwargs):
        """Generate mass status for reconciliation."""
        raise NotImplementedError(
            "DEX mass status requires successful authoritative venue queries",
        )

    # ─── TX RECEIPT HANDLER ────────────────────────────────────────────────────

    async def _wait_for_receipt(self, order: Order, tx_hash: str) -> None:
        """
        Wait for an authoritative transaction receipt.

        Unknown transport, parse, timeout, retry, and batch outcomes must remain
        unresolved per TC-E74–78. A terminal lifecycle event requires a parsed,
        authoritative receipt and incremental fill values.
        """
        raise NotImplementedError(
            "DEX receipt monitoring requires authoritative receipt parsing before lifecycle events",
        )

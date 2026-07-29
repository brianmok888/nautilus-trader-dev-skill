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

import asyncio

from nautilus_trader.cache.cache import Cache
from nautilus_trader.common.component import LiveClock, MessageBus
from nautilus_trader.common.config import NautilusConfig
from nautilus_trader.execution.messages import GenerateFillReports
from nautilus_trader.execution.messages import GenerateOrderStatusReport
from nautilus_trader.execution.messages import GenerateOrderStatusReports
from nautilus_trader.execution.messages import GeneratePositionStatusReports
from nautilus_trader.execution.reports import FillReport
from nautilus_trader.execution.reports import ExecutionMassStatus
from nautilus_trader.execution.reports import OrderStatusReport
from nautilus_trader.execution.reports import PositionStatusReport
from nautilus_trader.live.execution_client import LiveExecutionClient
from nautilus_trader.model.enums import (
    AccountType,
    OmsType,
)
from nautilus_trader.model.identifiers import (
    AccountId,
    ClientId,
    ClientOrderId,
    Venue,
)
from nautilus_trader.model.orders import Order

from ..dex_config import MyDEXExecClientConfig
from ..dex_instrument_provider import MyDEXInstrumentProvider


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
        loop: asyncio.AbstractEventLoop,
        client_id: ClientId,
        venue: Venue,
        account_id: AccountId,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        instrument_provider: MyDEXInstrumentProvider,
        config: MyDEXExecClientConfig,
    ) -> None:
        # The framework config deliberately records no operational fields: preserving
        # component lifecycle provenance is less important here than ensuring wallet
        # credentials can never enter serialization, logs, or component snapshots.
        super().__init__(
            loop=loop,
            client_id=client_id,
            venue=venue,
            oms_type=OmsType.NETTING,
            account_type=AccountType.CASH,
            base_currency=None,
            instrument_provider=instrument_provider,
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            config=(component_config := NautilusConfig()),
        )
        self._instrument_provider = instrument_provider
        self._component_config = component_config
        self._operational_config = config
        self._set_account_id(account_id)

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
            f"Connecting to MyDEX execution (wallet: {self._operational_config.wallet_address})"
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
        raise NotImplementedError(
            "DEX order modification requires an authoritative venue modify transaction",
        )

    async def _query_order(self, command) -> None:
        """Query order status by checking on-chain tx receipt."""
        raise NotImplementedError(
            "DEX order queries require an authoritative venue transaction query",
        )

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
        command: GenerateOrderStatusReport,
    ) -> OrderStatusReport | None:
        """
        Generate an order status report for reconciliation.

        Reconciliation follows TC-E84–87: only a successful authoritative venue
        query can establish order, fill, position, or zero-result state.
        """
        raise NotImplementedError(
            "DEX order reconciliation requires an authoritative venue transaction query",
        )

    async def generate_order_status_reports(
        self,
        command: GenerateOrderStatusReports,
    ) -> list[OrderStatusReport]:
        """Generate all available order status reports for reconciliation."""
        raise NotImplementedError(
            "DEX order reconciliation requires a successful authoritative venue query",
        )

    async def generate_fill_reports(self, command: GenerateFillReports) -> list[FillReport]:
        """Generate fill reports for reconciliation."""
        raise NotImplementedError(
            "DEX fill reconciliation requires parsed authoritative on-chain logs",
        )

    async def generate_position_status_reports(
        self,
        command: GeneratePositionStatusReports,
    ) -> list[PositionStatusReport]:
        """Generate position status reports for reconciliation."""
        raise NotImplementedError(
            "DEX position reconciliation requires a successful authoritative venue query",
        )

    async def generate_mass_status(
        self,
        lookback_mins: int | None = None,
    ) -> ExecutionMassStatus | None:
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

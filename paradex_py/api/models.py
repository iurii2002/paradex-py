from dataclasses import dataclass
from typing import Optional, TypedDict
from enum import Enum

import marshmallow_dataclass

from paradex_py.common.order import OrderSide, OrderStatus, OrderType, OrderLiquidity


@dataclass
class ApiError:
    error: str
    message: str
    data: Optional[dict]


@dataclass
class BridgedToken:
    name: str
    symbol: str
    decimals: int
    l1_token_address: str
    l1_bridge_address: str
    l2_token_address: str
    l2_bridge_address: str


@dataclass
class SystemConfig:
    starknet_gateway_url: str
    starknet_fullnode_rpc_url: str
    starknet_chain_id: str
    block_explorer_url: str
    paraclear_address: str
    paraclear_decimals: int
    paraclear_account_proxy_hash: str
    paraclear_account_hash: str
    oracle_address: str
    bridged_tokens: list[BridgedToken]
    l1_core_contract_address: str
    l1_operator_address: str
    l1_chain_id: str
    liquidation_fee: str


@dataclass
class AccountSummary:
    account: str
    initial_margin_requirement: str
    maintenance_margin_requirement: str
    account_value: str
    total_collateral: str
    free_collateral: str
    margin_cushion: str
    settlement_asset: str
    updated_at: int
    status: str
    seq_no: int


@dataclass
class Auth:
    jwt_token: str


ApiErrorSchema = marshmallow_dataclass.class_schema(ApiError)
SystemConfigSchema = marshmallow_dataclass.class_schema(SystemConfig)
AuthSchema = marshmallow_dataclass.class_schema(Auth)
AccountSummarySchema = marshmallow_dataclass.class_schema(AccountSummary)


class ParadexWebsocketChannel(Enum):
    """Enum class to define the channels for Paradex Websocket API.

    Attributes:
        ACCOUNT (str): Account channel
        BALANCE_EVENTS (str): Balance events channel
        BBO (str): Best Bid Offer channel
        FILLS (str): Fills channel
        FUNDING_DATA (str): Funding data channel
        FUNDING_PAYMENTS (str): Funding payments channel
        MARKETS_SUMMARY (str): Markets summary channel
        ORDERS (str): Orders channel
        ORDER_BOOK (str): Order book snapshots channel
        ORDER_BOOK_DELTAS (str): Order book deltas channel
        POINTS_DATA (str): Points data channel
        POSITIONS (str): Positions channel
        TRADES (str): Trades channel
        TRADEBUSTS (str): Tradebusts channel
        TRANSACTIONS (str): Transactions channel
        TRANSFERS (str): Transfers channel
    """

    ACCOUNT = "account"
    BALANCE_EVENTS = "balance_events"
    BBO = "bbo.{market}"
    FILLS = "fills.{market}"
    FUNDING_DATA = "funding_data.{market}"
    FUNDING_PAYMENTS = "funding_payments.{market}"
    MARKETS_SUMMARY = "markets_summary"
    ORDERS = "orders.{market}"
    ORDER_BOOK = "order_book.{market}.snapshot@15@100ms"
    ORDER_BOOK_DELTAS = "order_book.{market}.deltas"
    POINTS_DATA = "points_data.{market}.{program}"
    POSITIONS = "positions"
    TRADES = "trades.{market}"
    TRADEBUSTS = "tradebusts"
    TRANSACTIONS = "transaction"
    TRANSFERS = "transfers"



BBOData = TypedDict("BBOData", {'market': str, 'seq_no': int, 'ask': str, 'ask_size': str, 'bid': str, 'bid_size': str, 'last_updated_at': int})
BBOMsg = TypedDict("BBOMsg", {"channel": str, "data": BBOData})
PositionData = TypedDict("PositionData", {'id': str, 'market': str, 'status': OrderStatus, 'side': OrderSide, 'size': str, 'average_entry_price': str, 'average_entry_price_usd': str, 'average_exit_price': str, 'unrealized_pnl': str, 'unrealized_funding_pnl': str, 'cost': str, 'cost_usd': str, 'cached_funding_index': str, 'last_updated_at': int, 'created_at': int, 'last_fill_id': str, 'seq_no': int, 'liquidation_price': str, 'leverage': str, 'realized_positional_pnl': str, 'realized_positional_funding_pnl': str})
PositionMsg = TypedDict("PositionMsg", {"channel": str, "data": PositionData})
FillsData = TypedDict("FillsData", {'id': str, 'side': OrderSide, 'liquidity': OrderLiquidity, 'market': str, 'order_id': str, 'price': str, 'size': str, 'fee': str, 'fee_currency': str, 'created_at': int, 'remaining_size': str, 'client_id': str, 'fill_type': str, 'realized_pnl': str, 'realized_funding': str})
FillsMsg = TypedDict("FillsMsg", {"channel": str, "data": FillsData})

# todo add other msg typing if necessary
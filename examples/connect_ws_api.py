import asyncio
import os
import time

from starknet_py.common import int_from_hex

from paradex_py import Paradex
from paradex_py.api.models import PositionMsg, PositionData, FillsData, FillsMsg
from paradex_py.api.ws_client import ParadexWebsocketChannel
from paradex_py.environment import TESTNET

TEST_L1_ADDRESS = "0xd2c7314539dCe7752c8120af4eC2AA750Cf2035e"
TEST_L1_PRIVATE_KEY = "0xf8e4d1d772cdd44e5e77615ad11cc071c94e4c06dc21150d903f28e6aa6abdff"
TEST_L2_ADDRESS = "0x129c135ed63df9353885e292be4426b8ed6122b13c6c0e1bb787288a1f5adfa"
TEST_L2_PRIVATE_KEY = "0x543b6cf6c91817a87174aaea4fb370ac1c694e864d7740d728f8344d53e815"
TEST_L2_PUBLIC_KEY = "0x2c144d2f2d4fc61b6f8967f3ba0012a87d90140bcfe5a3e92e8df83258c960f"

LOG_FILE = os.getenv("LOG_FILE", "FALSE").lower() == "true"

if LOG_FILE:
    from paradex_py.common.file_logging import file_logger
    logger = file_logger
    logger.info("Using file logger")
else:
    from paradex_py.common.console_logging import console_logger

    logger = console_logger
    logger.info("Using console logger")

def fills_callback(ws_message: dict):
    message: FillsMsg = ws_message
    data:FillsData = message['data']
    print(data)

def position_callback(ws_message: dict):
    message: PositionMsg = ws_message
    data:PositionData = message['data']
    print(data)

def transfer_callback(ws_message: dict):
    print(ws_message)

def main():
    paradex = Paradex(
        env=TESTNET,
        l1_address=TEST_L1_ADDRESS,
        l1_private_key=TEST_L1_PRIVATE_KEY,
        l2_private_key=TEST_L2_PRIVATE_KEY,
        logger=logger,
        skip_ws=False,
    )

    fills_channel = ParadexWebsocketChannel.FILLS
    positions_channel = ParadexWebsocketChannel.POSITIONS
    transfer_channel = ParadexWebsocketChannel.TRANSFERS
    params = {'market': 'ETH-USD-PERP'}

    print('Subscribe to FILLS')
    sub_id_fills = paradex.ws_subscribe(channel=fills_channel, callback=position_callback, params=params)
    time.sleep(5)

    print('Subscribe to POSITIONS')
    sub_id_position = paradex.ws_subscribe(channel=positions_channel, callback=position_callback)
    time.sleep(5)

    print('Subscribe to TRANSFERS')
    sub_id_transfer = paradex.ws_subscribe(channel=transfer_channel, callback=transfer_callback)
    time.sleep(5)

    print('Unsubscribe from TRANSFERS')
    paradex.ws_unsubscribe(channel=transfer_channel, subscription_id=sub_id_transfer)
    time.sleep(5)

    print('Unsubscribe from FILLS')
    paradex.ws_unsubscribe(channel=fills_channel, subscription_id=sub_id_fills, params=params)
    time.sleep(5)

    print('Unsubscribe from POSITIONS')
    paradex.ws_unsubscribe(channel=positions_channel, subscription_id=sub_id_position)

if __name__ == '__main__':
    main()
import json
import logging
import time
import threading
import websocket

from typing import Callable, Dict, Optional, List, Tuple, NamedTuple, Any
from collections import defaultdict

from paradex_py.account.account import ParadexAccount
from paradex_py.api.models import ParadexWebsocketChannel
from paradex_py.environment import Environment


ActiveSubscription = NamedTuple("ActiveSubscription",
                                [("callback", Callable[[Any], None]), ("subscription_id", int)])


class ParadexWebsocketClient(threading.Thread):
    classname: str = "ParadexWebsocketClient"

    def __init__(self, env: Environment, logger: Optional[logging.Logger] = None, account:ParadexAccount = None):
        super().__init__()
        self.env = env
        self.api_url = f"wss://ws.api.{self.env}.paradex.trade/v1"
        self.logger = logger or logging.getLogger(__name__)
        self.ws_ready = False
        self.account:Optional[ParadexAccount] = account
        self.queued_subscriptions: List[Tuple[ParadexWebsocketChannel, Dict, ActiveSubscription]] = []
        self.active_subscriptions: Dict[str, List[ActiveSubscription]] = defaultdict(list)
        self.subscription_id_counter = 0

        self.bearer_header = None
        if self.account:
            self.bearer_header = {"Authorization": f"Bearer {self.account.jwt_token}"}

        self.ws = websocket.WebSocketApp(self.api_url, on_message=self.read_messages, on_open=self.on_open, header=self.bearer_header)
        self.ping_sender = threading.Thread(target=self.send_ping)

    def run(self):
        self.ping_sender.start()
        self.ws.run_forever()

    def send_ping(self):
        while True:
            time.sleep(50)
            logging.debug("Websocket sending ping")
            self.ws.send(json.dumps({"method": "ping"}))

    def on_open(self, _ws):
        logging.debug("on_open")
        self.ws_ready = True
        if self.account:
            self.send_auth_id()
        for channel, params, active_subscription in self.queued_subscriptions:
            self.subscribe(channel=channel, callback=active_subscription.callback,
                           subscription_id=active_subscription.subscription_id, params=params)

    def send_auth_id(self) -> None:
        """
        Sends an authentication message to the Paradex WebSocket.
        """
        self.ws.send(
            json.dumps(
                {
                    "id": int(time.time() * 1_000_000),
                    "jsonrpc": "2.0",
                    "method": "auth",
                    "params": {"bearer": self.account.jwt_token},
                }
            )
        )
        self.logger.info(f"{self.classname}: Authenticated to {self.api_url}")

    def read_messages(self, _ws, message):
        if message == "Websocket connection established.":
            logging.debug(message)
            return

        logging.debug(f"on_message {message}")
        ws_msg = json.loads(message)

        if "params" not in ws_msg:
            self.logger.debug(f"{self.classname}: Non-actionable message:{ws_msg}")
        else:
            data = ws_msg['params']
            channel_with_params = data.get("channel")

            if channel_with_params == "pong":
                logging.debug("Websocket received pong")
                return
            if channel_with_params is None:
                logging.debug(f"Could not handle message with data - {data}")
                return

            active_subscriptions = self.active_subscriptions[channel_with_params]
            if len(active_subscriptions) == 0:
                logging.info("Websocket message from an unexpected subscription:", message, channel_with_params)
                logging.info("Probably it was already closed")
            else:
                for active_subscription in active_subscriptions:
                    active_subscription.callback(data)

    def subscribe(
        self, channel: ParadexWebsocketChannel, callback: Callable[[Any], None],
            subscription_id: Optional[int] = None, params: Optional[dict] = None
    ) -> int:
        if subscription_id is None:
            self.subscription_id_counter += 1
            subscription_id = self.subscription_id_counter

        if params is None:
            params = {}
        channel_with_params = channel.value.format(**params)

        if not self.ws_ready:
            logging.debug("enqueueing subscription")
            self.queued_subscriptions.append((channel, params, ActiveSubscription(callback, subscription_id)))
        else:
            logging.debug("subscribing")
            if channel_with_params in ["account", "balance_events", 'markets_summary', 'positions', 'tradebusts',
                                       'transaction', 'transfers']:
                if len(self.active_subscriptions[channel_with_params]) != 0:
                    raise NotImplementedError(f"Cannot subscribe to {channel_with_params} multiple times")
            self.active_subscriptions[channel_with_params].append(ActiveSubscription(callback, subscription_id))
            self.logger.info(f"{self.classname}: Subscribe channel:{channel_with_params} params:{params} callback:{callback}")
            self.ws.send(json.dumps({
                    "id": int(time.time() * 1_000_000),
                    "jsonrpc": "2.0",
                    "method": "subscribe",
                    "params": {"channel": channel_with_params},
                }))
        return subscription_id

    def unsubscribe(self, channel: ParadexWebsocketChannel, subscription_id: int, params: Optional[dict] = None) -> bool:
        if not self.ws_ready:
            raise NotImplementedError("Can't unsubscribe before websocket connected")
        if params is None:
            params = {}
        channel_with_params = channel.value.format(**params)
        active_subscriptions = self.active_subscriptions[channel_with_params]

        new_active_subscriptions = [x for x in active_subscriptions if x.subscription_id != subscription_id]
        if len(new_active_subscriptions) == 0:
            self.ws.send(json.dumps(                {
                    "id": int(time.time() * 1_000_000),
                    "jsonrpc": "2.0",
                    "method": "unsubscribe",
                    "params": {"channel": channel_with_params},
                }))
        self.active_subscriptions[channel_with_params] = new_active_subscriptions
        return len(active_subscriptions) != len(new_active_subscriptions)

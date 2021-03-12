import time
import logging as log

import requests
import obswebsocket
import obswebsocket.exceptions
import obswebsocket.requests
import cmpc.twitch_message


class CommandLogging:
    # todo: check if source exists or if read from file is on
    def __init__(self, bot, obs_file_name, obs_log_sleep_duration=None, obs_none_log_msg=None, use_websockets=True):
        self.bot = bot
        self.obs_file_name = obs_file_name
        if obs_log_sleep_duration is None:
            obs_log_sleep_duration = 0.5
        self.obs_log_sleep_duration = obs_log_sleep_duration
        if obs_none_log_msg is None:
            obs_none_log_msg = 'nothing'
        self.obs_none_log_msg = obs_none_log_msg

        self._socket = obswebsocket.obsws('localhost', 4444)
        if use_websockets:
            try:
                self._socket.connect()
                text_source = self._socket.call(obswebsocket.requests.GetTextGDIPlusProperties('Executing'))
                if not text_source.status:
                    log.error("Couldn't get obs text source: Executing. Defaulting to executing.txt")
                if text_source.datain['read_from_file']:
                    log.error('')
            except obswebsocket.exceptions.ConnectionFailure:
                log.error('Could not connect to obs websocket, defaulting to executing.txt')
                self.obs_log_handler = self._obs_log_executing_txt
            else:
                self.obs_log_handler = self._obs_log_ws
        else:
            self.obs_log_handler = self._obs_log_executing_txt

    def log_to_discord(self, message: cmpc.twitch_message.TwitchMessage):
        requests.post(self.bot.config['discord']['chatrelay'],
                      json=message.get_log_webhook_payload(),
                      headers={'User-Agent': self.bot.config['api']['useragent']})

    def _obs_log_executing_txt(self, obs_log_text):
        with open(self.obs_file_name, 'w', encoding='utf-8') as obs_file_handle:
            obs_file_handle.write(obs_log_text)

    def _obs_log_ws(self, obs_log_text):
        try:
            self._socket.call(obswebsocket.requests.SetTextGDIPlusProperties('Executing', text=obs_log_text))
        except obswebsocket.exceptions.ConnectionFailure:
            log.error('Could not connect to obs websocket, defaulting to executing.txt')
            self._socket.disconnect()
            self._obs_log_executing_txt(obs_log_text)
            self.obs_log_handler = self._obs_log_executing_txt

    def log_to_obs(
            self, message: cmpc.twitch_message.TwitchMessage, none_log_msg=None, sleep_duration=None, none_sleep=False
    ):
        """Log a message to the file shown on-screen for the stream."""
        if none_log_msg is None:
            none_log_msg = self.obs_none_log_msg
        if sleep_duration is None:
            sleep_duration = self.obs_log_sleep_duration

        if message is None:
            self.obs_log_handler(none_log_msg)
            if none_sleep:
                time.sleep(sleep_duration)
        else:
            self.obs_log_handler(message.get_log_string())

            time.sleep(sleep_duration)
            log.info(message.get_log_string())
            self.log_to_discord(message)

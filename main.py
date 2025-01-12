import base64
import ctypes
import string
import sys
from turtle import width

from src.base import AbsoluteBase
from src.utils import utils
from src.solver import solver
from charlogger import Logger
import time, threading, websocket, json, random, os
import pystyle


width = os.get_terminal_size().columns
a = [pystyle.Colors.blue_to_cyan, pystyle.Colors.cyan_to_blue]
def connectToWebsocket(token: str) -> None:
        jsn = {
            "op":2,
            "d":{
                "token":token,
                "capabilities":61,
                "properties":{
                    "os":"Windows",
                    "browser":"Chrome",
                    "device":"",
                    "system_locale":"en-US",
                    "browser_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                    "browser_version":"108.0.0.0",
                    "os_version":"10",
                    "referrer":"",
                    "referring_domain":"",
                    "referrer_current":"",
                    "referring_domain_current":"",
                    "release_channel":"stable",
                    "client_build_number":"",
                    "client_event_source":"null"
                },
                "presence":{
                    "status":"dnd",
                    "since":0,
                    "activities":[],
                    "afk": True
                },
                "compress": False,
                "client_state":{
                    "guild_hashes":{},
                    "highest_last_message_id": "0",
                    "read_state_version": 0,
                    "user_guild_settings_version": -1
                }
            }
        }

        ws = websocket.WebSocket()
        ws.connect("wss://gateway.discord.gg/?encoding=json&v=9")
        resp = ws.recv()
        event = json.loads(resp)
        ws.send(json.dumps(jsn))


class creator(AbsoluteBase):
    def __init__(self, taskId: int, invite: str) -> None:
        super().__init__(taskId)
        self.invite = invite
        self.username = utils.getUsername()
        pass

    
    def start(self) -> None:
        self.session.headers = self.getHeaders()
        self.captchaToken = solver.solveCaptcha(self.logger, self.session)
        self.fingerprint = self.getFingerprint()        
        self.session.headers["X-Fingerprint"] = self.fingerprint
        self.getCookies()
        self.register()

    def register(self):
        body = {
            "fingerprint":  self.fingerprint,
            "username": self.username,
            "invite": self.invite,
            "consent": True,
            "gift_code_sku_id": None,
            "captcha_key": self.captchaToken
        }

        headers = {
            "accept": "*/*",
	        "accept-encoding": "gzip, deflate, br",
	        "accept-language": "en-US,en;q=0.9",
	        "content-type": "application/json",
	        "cookie": self.getCookies(),
	        "origin": "https",
	        "referer": "https",
            "Sec-ch-ua": '"Chromium";v="112", "Not A(Brand";v="24", "Google Chrome";v="112"',
	        "sec-ch-ua-mobile": "?0",
	        "Sec-ch-ua-platform": "\"Windows\"",
	        "sec-fetch-dest": "empty",
	        "sec-fetch-mode": "cors",
	        "sec-fetch-site": "same-origin",
	        "user-agent": self.userAgent,
	        "x-debug-options": "bugReporterEnabled",
	        "x-discord-locale": "en-US",
	        "x-fingerprint": self.fingerprint,
	        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExMi4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTEyLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiJodHRwczovL3d3dy5nb29nbGUuY29tLyIsInJlZmVycmluZ19kb21haW4iOiJ3d3cuZ29vZ2xlLmNvbSIsInNlYXJjaF9lbmdpbmUiOiJnb29nbGUiLCJyZWZlcnJlcl9jdXJyZW50IjoiaHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8iLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiJ3d3cuZ29vZ2xlLmNvbSIsInNlYXJjaF9lbmdpbmVfY3VycmVudCI6Imdvb2dsZSIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjE5MDE4NywiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=",
}
        resp = self.post("https://discord.com/api/v9/auth/register",json=body,headers=headers)
        body = {
                "consent": "true",
                "fingerprint": self.fingerprint,
                "invite": self.invite,
                "username": self.username,
                "captcha_key": self.captchaToken
            }
        if "token" in resp.text:
            self.token = resp.json()["token"]
            self.logger.valid(title="CREATED", data=f"{self.token}")
            with open("output/tokens.txt", "a") as f:
                f.write(f"{self.token}\n")
                f.close()
            threading.Thread(target=connectToWebsocket(self.token),args=(self.token,)).start()
            self.session.headers["authorization"] = self.token
        elif "retry_after" in resp.text:
            delay = resp.json()["retry_after"]
            self.logger.warn(title="RATELIMIT", data=f"Waiting for {delay}s...")
            time.sleep(delay)
        elif "invalid-response" or "invalid-input-response" in resp.text:
            self.logger.warn(title="ERROR", data=f"Captcha error: {self.captchaSolution.split('.')[0]}")
            
    def getHeaders(self) -> dict:
        headers = {
	        "accept": "*/*",
	        "accept-encoding": "gzip, deflate, br",
	        "accept-language": "en-US,en;q=0.9",
	        "content-type": "application/json",
	        "origin": "https",
	        "referer": "https",
            "cookie": self.getCookies(),
            "Sec-ch-ua": '"Chromium";v="112", "Not A(Brand";v="24", "Google Chrome";v="112"',
	        "sec-ch-ua-mobile": "?0",
	        "Sec-ch-ua-platform": "\"Windows\"",
	        "sec-fetch-dest": "empty",
	        "sec-fetch-mode": "cors",
	        "sec-fetch-site": "same-origin",
	        "user-agent": self.userAgent,
            #"x-fingerprint": self.fingerprint,
	        "x-debug-options": "bugReporterEnabled",
	        "x-discord-locale": "en-US",
	        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExMi4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTEyLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiJodHRwczovL3d3dy5nb29nbGUuY29tLyIsInJlZmVycmluZ19kb21haW4iOiJ3d3cuZ29vZ2xlLmNvbSIsInNlYXJjaF9lbmdpbmUiOiJnb29nbGUiLCJyZWZlcnJlcl9jdXJyZW50IjoiaHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8iLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiJ3d3cuZ29vZ2xlLmNvbSIsInNlYXJjaF9lbmdpbmVfY3VycmVudCI6Imdvb2dsZSIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjE5MDE4NywiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=",
}
        return headers

        
        
    def getCookies(self) -> None:
        self.get("https://discord.com/register")
        self.logger.debug(f"Got cookies.")

    def getFingerprint(self) -> str:
        return self.get("https://discord.com/api/v9/experiments").json()["fingerprint"]


config = json.loads(open("data/config.json").read())
invite = config.get("general").get("invite")
threads = config.get("general").get("threads")

if invite.startswith("https://discord.gg/"):
    invite = invite.split("https://discord.gg/")[1]

def runThread(threadNum: int):
    while True:
        creator(threadNum, invite).start()

def main():
    logger = Logger(True, defaultPrefix=f"<TIME> GENERATOR")
    os.system("cls")
    if not os.path.exists("output"): os.mkdir("output")
    logger.info(f"Starting generator...")
    for x in range(threads):
        thread = threading.Thread(target=runThread, args=(x + 1,))
        thread.start()

if __name__ == "__main__":
    main()

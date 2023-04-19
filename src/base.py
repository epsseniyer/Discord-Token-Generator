import random, tls_client, tls_client.response
from charlogger import Logger

class AbsoluteBase():

    def __init__(self, taskId: int) -> None:
        self.taskId = taskId
        prefixStr = f"{taskId}"
        if taskId < 100:
            if taskId < 10:prefixStr = f"00{taskId}"
            else: prefixStr = f"0{taskId}"
        self.logger = Logger(False, defaultPrefix=f"<TIME> WORKER-{prefixStr}")
        self.session = self.getClient()

        proxies = [x.strip() for x in open("data/proxies.txt", "r", encoding="utf8").readlines()]
        self.proxy = f"http://{random.choice(proxies)}"
        self.session.proxies = { "http": self.proxy, "https": self.proxy }

        self.userAgent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"

        self.session.headers = {
            # "User-Agent": self.userAgent['user_agent']
            "User-Agent": self.userAgent
        }
        pass

    def post(self, url, *args, **kwargs) -> tls_client.response.Response:
        return self.session.post(url, *args, **kwargs)

    def get(self, url, *args, **kwargs) -> tls_client.response.Response:
        return self.session.get(url, *args, **kwargs)

    def put(self, url, *args, **kwargs) -> tls_client.response.Response:
        return self.session.put(url, *args, **kwargs)
    
    def patch(self, url, *args, **kwargs) -> tls_client.response.Response:
        return self.session.patch(url, *args, **kwargs)

    def getOptions(self, headers: dict = None):
        if headers is None:
            headers = {}
        headers.update(self.session.headers)
    
    def getClient(self) -> tls_client.Session:
        chrome_v = 110
        return tls_client.Session(
            f"chrome_{str(chrome_v)}",
            ja3_string= "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-17513,29-23-24,0",
            h2_settings={"HEADER_TABLE_SIZE": 65536,"MAX_CONCURRENT_STREAMS": 1000,"INITIAL_WINDOW_SIZE": 6291456,"MAX_HEADER_LIST_SIZE": 262144},
            h2_settings_order=["HEADER_TABLE_SIZE","MAX_CONCURRENT_STREAMS","INITIAL_WINDOW_SIZE","MAX_HEADER_LIST_SIZE"],
            supported_signature_algorithms=["ECDSAWithP256AndSHA256","PSSWithSHA256","PKCS1WithSHA256","ECDSAWithP384AndSHA384","PSSWithSHA384","PKCS1WithSHA384","PSSWithSHA512","PKCS1WithSHA512",],
            supported_versions=["GREASE", "1.3", "1.2"],
            key_share_curves=["GREASE", "X25519"],
            cert_compression_algo="brotli",
            pseudo_header_order=[":authority",":method",":path",":scheme"],
            connection_flow=15663105,
            header_order=["accept","user-agent","accept-encoding","accept-language"],
            random_tls_extension_order=True)
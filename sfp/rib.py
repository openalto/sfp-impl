from sfp.definitions import SFPDefinition
import json


class RibItem:
    def __init__(self, src_ip="*", dst_ip="*", src_port="*", dst_port="*", protocol="*", egress_port=None,
                 peer_speaker=None, inner=False, path=None):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port
        self.protocol = protocol
        self.path = path or [Rib.DOMAIN_NAME]

        self.egress_port = egress_port
        self.peer_speaker = peer_speaker
        self.inner = inner

    def match(self, src_ip, dst_ip, src_port, dst_port, protocol):
        if self.src_ip != '*' and not self.src_ip.startswith(src_ip): # TODO: change this
            return False
        if self.dst_ip != '*' and not self.dst_ip.startswith(dst_ip): # TODO: change this
            return False
        if self.src_port != '*' and self.src_port != src_port:
            return False
        if self.dst_port != '*' and self.dst_port != dst_port:
            return False
        if self.protocol != '*' and self.protocol != protocol:
            return False
        return True


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Rib(object, metaclass=Singleton):
    DOMAIN_NAME = ""
    rib = []
    peer_list = []
    initialized = False

    @staticmethod
    def initialize():
        if not Rib.initialized:
            Rib.initialized = True
            Rib.read_from_file()


    @staticmethod
    def read_from_file(file_path=SFPDefinition.INITIAL_RIB_FILE):
        contents = open(file_path, 'r').read()
        obj = json.loads(contents)
        Rib.DOMAIN_NAME = obj["domain-name"]
        for cidr in obj["inner-cidr"]:
            rib_item = RibItem(dst_ip=cidr, inner=True)
            Rib.rib.append(rib_item)

        for peer in obj["peers"]:
            Rib.peer_list.append(peer)


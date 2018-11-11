import json
import requests
import falcon
import logging

from sfp.rib import Rib, RibItem

logging.basicConfig(filename='sfp.log', level=logging.DEBUG)


class QueryEntry(object):

    def on_post(self, req, resp):
        """
        input format
        {
            "input": {
                "src-ip": <src-ip>,
                "dst-ip": <dst-ip>,
                "protocol": <protocol>,
                "src-port": <src-port>, #Optional
                "dst-port": <dst-port> #Optional
            }
        }
        """
        Rib.initialize()
        obj = json.loads(req.stream.read())["input"]
        if "src-port" not in obj:
            obj["src-port"] = None
        if "dst-port" not in obj:
            obj["dst-port"] = None

        ribItems = Rib.rib
        for ribItem in ribItems:
            if ribItem.match(obj["src-ip"], obj["dst-ip"], obj["src-port"], obj["dst-port"], obj["protocol"]):
                logging.info("Match local rib successfully")
                resp.body = json.dumps({"result": True, "path": ribItem.path})
                resp.status = falcon.HTTP_200
                return
        remote_ip = req.remote_addr
        peer_list = Rib.peer_list
        for peer in peer_list:
            logging.debug("Finding " + obj["dst-ip"] + " in peer: " + peer)
            ip = peer.split(":")[0]  # WARN: loop maybe
            if ip != remote_ip:
                url = "http://" + peer + "/query"
                logging.debug("Send request to " + url)
                r = requests.post(url, json={"input": obj})
                ret_obj = json.loads(r.text)
                logging.debug("Get response from " + peer + ": " + str(obj))
                if ret_obj["result"]:
                    logging.info("Found in " + peer)
                    src_port = obj.get("src-port") or "*"
                    dst_port = obj.get("dst-port") or "*"
                    full_path = [Rib.DOMAIN_NAME] + ret_obj["path"]
                    Rib.rib.append(RibItem(src_ip=obj["src-ip"], dst_ip=obj["dst-ip"], src_port=src_port,
                                            dst_port=dst_port, protocol=obj["protocol"], inner=False,
                                            peer_speaker=peer, path=full_path))
                    resp.status = falcon.HTTP_200
                    resp.body = json.dumps({"result": True, "path": full_path})
                    return
                logging.info("Not found in " + peer)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({"result": False})


class PeerRegisterEntry(object):
    """
    input format
    {
        "address": "192.168.1.1:8399"
    }
    """

    def on_post(self, req, resp):
        obj = json.loads(req.stream.read)
        addr = obj["address"]
        Rib.peer_list.append(addr)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({"result": True})


class PathQueryEntry():
    pass

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
        obj = json.loads(req.stream.read())["input"]
        if "src-port" not in obj:
            obj["src-port"] = None
        if "dst-port" not in obj:
            obj["dst-port"] = None

        ribItems = Rib().rib
        result = False
        for ribItem in ribItems:
            if ribItem.match(obj["src-ip"], obj["dst-ip"], obj["src-port"], obj["dst-port"], obj["protocol"]):
                logging.info("Match local rib successfully")
                result = True
                break
        if result:
            resp.status = falcon.HTTP_200
            resp.body = json.dumps({"result": result, "path": [Rib().domain_name]})
            return
        remote_ip = req.remote_addr
        peer_list = Rib().peer_list
        for peer in peer_list:
            logging.debug("Finding " + obj["dst-ip"] + " in peer: " + peer)
            ip = peer.split(":")[0]  # WARN: loop maybe
            if ip != remote_ip:
                url = "http://" + peer + "/query"
                logging.debug("Send request to " + url)
                r = requests.post(url, json={"input": obj})
                obj = json.loads(r.text)
                if obj["result"]:
                    logging.info("Found in " + peer)
                    ribItems.append(RibItem(src_ip=obj["src-ip"], dst_ip=obj["dst-ip"], src_port=obj["src-port"],
                                            dst_port=obj["dst-port"], protocol=obj["protocol"], inner=False,
                                            peer_speaker=peer))
                    resp.status = falcon.HTTP_200
                    resp.body = json.dumps({"result": True, "path": [Rib().domain_name] + obj["path"]})
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
        Rib().peer_list.append(addr)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({"result": True})

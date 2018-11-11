import json
import requests
import falcon

from sfp.rib import Rib, RibItem


class QueryEntry(object):
    """
    input format
    {
        "input": [
            {
                "src_ip": <src_ip>,
                "dst_ip": <dst_ip>,
                "protocol": <protocol>,
                "src_port": <src_port>, #Optional
                "dst_port": <dst_port> #Optional
            }
        ]
    }
    """

    def on_post(self, req, resp):
        obj = json.loads(req.stream.read())
        if "src_port" not in obj:
            obj["src_port"] = None
        if "dst_port" not in obj:
            obj["dst_port"] = None

        ribItems = Rib().rib
        result = False
        for ribItem in ribItems:
            if ribItem.match(obj["src_ip"], obj["dst_ip"], obj["src_port"], obj["dst_port"], obj["protocol"]):
                result = True
                break
        if result:
            resp.status = falcon.HTTP_200
            resp.body = json.dumps({"result": result, "path": [Rib().domain_name]})
            return
        remote_ip = req.remote_addr
        peer_list = Rib().peer_list
        for peer in peer_list:
            ip = peer.split(":")[0]  # WARN: loop maybe
            if ip != remote_ip:
                r = requests.post("http://" + peer + "/query", json=obj)
                obj = json.loads(r.text)
                if obj["result"]:
                    ribItems.append(RibItem(src_ip=obj["src_ip"], dst_ip=obj["dst_ip"], src_port=obj["src_port"],
                                            dst_port=obj["dst_port"], protocol=obj["protocol"], inner=False,
                                            peer_speaker=peer))
                    resp.status = falcon.HTTP_200
                    resp.body = json.dumps({"result": True, "path": [Rib().domain_name] + obj["path"]})
                    return
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

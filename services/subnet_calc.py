import ipaddress

def calculate_subnet(cidr):
    try:
        net = ipaddress.ip_network(cidr, strict=False)
        return {
            "network": str(net.network_address),
            "broadcast": str(net.broadcast_address),
            "netmask": str(net.netmask),
            "first_host": str(list(net.hosts())[0]),
            "last_host": str(list(net.hosts())[-1]),
            "usable_hosts": net.num_addresses - 2
        }
    except Exception as e:
        return {"error": str(e)}
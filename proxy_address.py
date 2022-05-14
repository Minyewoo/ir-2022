'''stores data for connection with proxy server'''

class ProxyAddress:
    '''stores data for connection with proxy server'''

    def __init__(self, ip_address: str, port: int, protocol: str):
        self.ip_address = ip_address
        self.port = port
        self.protocol = protocol

    def as_map(self) -> map:
        return {self.protocol : str(self)}

    def __str__(self) -> str:
        return f'{self.protocol}://{self.ip_address}:{self.port}'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.ip_address)

    def __eq__(self, other):
        if isinstance(other, ProxyAddress):
            return self.ip_address == other.ip_address
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

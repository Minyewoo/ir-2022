'''stores data for connection with proxy server'''


class ProxyAddress:
    '''stores data for connection with proxy server'''
    ip_address_key = 'ip_address'
    port_key = 'port'
    protocol_key = 'protocol'

    def __init__(self, ip_address: str, port: int, protocol: str):
        self.ip_address = ip_address
        self.port = port
        self.protocol = protocol

    def as_map(self) -> map:
        '''transforms proxy address to map object wich can be used with requests package'''
        return {self.protocol: str(self)}

    def to_json(self) -> map:
        '''transforms proxy address to map object'''
        return {
            self.ip_address_key: self.ip_address,
            self.port_key: self.port,
            self.protocol_key: self.protocol,
        }

    @staticmethod
    def from_json(json: map):
        '''build proxy address from map object'''
        return ProxyAddress(
            json[ProxyAddress.ip_address_key],
            json[ProxyAddress.port_key],
            json[ProxyAddress.protocol_key]
        )

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

class _Dce(object):
    def connect(self):
        pass

    def bind(self, uuid):
        pass


class _Transport(object):
    def __init__(self, string):
        self.string = string

    def set_smb_connection(self, smb):
        self.smb = smb

    def get_dce_rpc(self):
        return _Dce()


def DCERPCTransportFactory(string):
    return _Transport(string)

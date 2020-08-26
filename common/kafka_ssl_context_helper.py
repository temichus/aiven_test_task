from aiokafka.helpers import create_ssl_context

def get_ssl_context(cafile,certfile,keyfile):
    return create_ssl_context(
        cafile=cafile,  # CA used to sign certificate.
                             # `CARoot` of JKS store container
        certfile=certfile,  # Signed certificate
        keyfile=keyfile,  # Private Key file of `certfile` certificate
        )
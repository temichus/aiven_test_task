from aiokafka.helpers import create_ssl_context


def get_ssl_context(cafile, certfile, keyfile):
    """
    create ssl context
    :param cafile: CA used to sign certificate.
    :param certfile: Signed certificat
    :param keyfile: Private Key file of `certfile` certificate
    :return:
    """
    return create_ssl_context(
        cafile=cafile,
        certfile=certfile,
        keyfile=keyfile,
    )

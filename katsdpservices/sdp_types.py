"""Various resolvers, type definitions and enum used across the SDP system."""


STREAM_TYPES = {'sdp_l0': 'sdp.l0',
                'sdp_l1_flags': 'sdp.flags'
                }


def stream_type(stream_name):
    """Attempt to resolve the supplied stream_name to a stream type.
    TODO: This is a very naive implementation and will need improvement.
    """
    return STREAM_TYPES.get(stream_name, stream_name.replace("_", "."))

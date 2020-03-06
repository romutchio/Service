from uuid import UUID


def is_valid_uuid(uuid, version=4):
    try:
        UUID(uuid, version=version)
        return True
    except ValueError:
        return False


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False



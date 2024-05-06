import re


def build_dict_public_properties(
        obj: object, 
        pattern=r"^[^_]+[0-9A-Za-z_]+[^_]+$"
) -> dict:
    return {
        slot: getattr(obj, slot) for slot in dir(obj)
        if re.fullmatch(pattern, slot) and getattr(obj, slot) is not None
    }

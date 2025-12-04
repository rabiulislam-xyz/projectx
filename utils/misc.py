def convert_to_bool(param, nullable=False):
    if param in ["true", "True", True, "yes", "Yes"]:
        return True

    if nullable:
        if param in ["null", "None", None]:
            return None

    return False

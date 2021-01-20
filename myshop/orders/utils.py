def convert_bool_to_yes_or_no(value):
    if value is True:
        value = "Paid"
    else:
        value = "Pending payment"
    return value

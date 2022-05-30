def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return get_instance


class Temp:
    pass


def get_secure_num(data, key) -> float:
    if key in data.keys():
        value = data[key]
        if value not in [None, False, '']:
            try:
                value = float(value)
            except:
                value = value.replace(',', '.')
                try:
                    value = float(value)
                except:
                    return 0.0
            return value
    else:
        return 0.0


def get_switch_state(data, key) -> bool:
    if key in data.keys():
        if data[key] == 'on':
            return True
        elif data[key] == 'checked':
            return True
        else:
            return False
    else:
        return False

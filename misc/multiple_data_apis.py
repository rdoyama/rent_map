from configparser import SectionProxy


def get_all_apis(config: SectionProxy) -> list[str]:
    key_base = "data_api"
    apis = []
    for i in range(1, 10):
        try:
            if config[f"{key_base}_{i}"].startswith("https"):
                apis.append(config[f"{key_base}_{i}"])
            else:
                return apis
        except KeyError:
            return apis
    return apis
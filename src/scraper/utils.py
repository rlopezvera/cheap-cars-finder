def clean_link(link: str) -> str:
    return link.replace("venta-de-autos-usados/", "")


def check_length_of_one(*args) -> bool:
    # evaluate that all of the args are of length 1
    return all([len(arg) == 1 for arg in args])

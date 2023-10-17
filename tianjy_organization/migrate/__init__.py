from .doctype import run as doctype
from .organization_member import run as organization_member


def run():
    doctype()
    organization_member()

import logging
from antispam.libs.shared.substitute_args import SubstituteArgs
from antispam.libs.shared.base import Base

__all__ = ("SubstituteArgs", "Base")

logging.getLogger(__name__).addHandler(logging.NullHandler())

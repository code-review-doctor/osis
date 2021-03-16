from base.ddd.utils.business_validator import BusinessValidator
from osis_common.ddd import interface


class ReqiredFields(BusinessValidator):

    def __init__(self, command: interface.CommandRequest):
       pass

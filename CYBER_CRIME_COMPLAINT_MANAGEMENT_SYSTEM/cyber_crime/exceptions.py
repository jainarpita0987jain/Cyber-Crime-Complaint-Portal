class CyberCrimeError(Exception):
    pass


class ComplaintNotFoundError(CyberCrimeError):
    pass


class InvalidComplaintError(CyberCrimeError):
    pass

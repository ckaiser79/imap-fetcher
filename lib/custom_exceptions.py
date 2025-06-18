
class UnparseableEmailException(Exception):
    
    def __init__(self, message="The email could not be parsed."):
        self.message = message
        super().__init__(self.message)
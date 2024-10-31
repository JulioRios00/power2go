class UserAlreadyExistsError(Exception):
		pass

class UserNotFoundError(Exception):
		pass

class UserHasContractsError(Exception):
		def __init__(self, message="User has contract(s) and cannot be deleted"):
				self.message = message
				super().__init__(self.message)
  
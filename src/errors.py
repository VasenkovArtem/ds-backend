class Error:
    """
    Describes a special type of error, which includes a unique code
    for the most possible types of errors, a description of the error,
    and an HTTP code for the returned response. It is possible
    to change the default message during initialization

    Attributes
    ----------
    code : int
        code of created error
    message : str
        string with description of the error

    Methods
    -------
    return_error()
        Returns an error as a dictionary with the error message
        and the http type of returned response
    """

    ERRORS = {
        0: ('field not found', 400),
        1: ('invalid image', 400),
        2: ('image not found', 404),
        3: ('service with images unavailable', 424),
        4: ('invalid access to the service with images', 500),
        5: ('invalid image id', 400),
        6: ('image not in byte format', 415),
        7: ('invalid number of parameters of returned json', 500),
        8: ('unknown error', 500)
    }

    def __init__(self, code: int, message: str = None):
        """
        Initializes the Error instance
        :param code: int, error type number to generate
        :param message: str, optional, message for the specified error
        if there is a necessary to specify it
        and not use the default message for the type
        """
        if code not in self.ERRORS:
            self.code = 8
        else:
            self.code = code
        if message:
            self._message = message

    @property
    def message(self) -> str:
        """
        Returns the message passed when the error was initialized,
        and if there was none, the default message for the given error type
        """
        if hasattr(self, '_message'):
            return self._message
        return self.ERRORS[self.code][0]

    def return_error(self) -> (dict, int):
        """
        Returns an error as a dictionary with the error message
        and the http type of returned response
        :return: tuple(dict, int), error message as value in dictionary
        and int number of the http type of returned response
        """
        message, status = self.ERRORS[self.code]
        if hasattr(self, '_message'):
            message = self._message
        return {'error': message}, status

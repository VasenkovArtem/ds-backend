from models.plate_reader import PlateReader, InvalidImage
from errors import Error
from typing import Union, Any, Hashable
import io
import requests
import logging


IMAGES_SERVER = 'http://51.250.83.169:7878/images'


def check_img_id_valid(img_id: str) -> bool:
    """
    Checks if the string passed as a parameter is valid for id.
    It's considered that id is a natural number,
    so the string must consist only of digits and not start from zero
    :param img_id: str, string will be validate for id
    :return: bool, result of checking - True if string can be a valid id,
    False otherwise
    """
    # if there is at least one non-numeric character or starts from zero
    if not img_id.isdecimal() or img_id[0] == '0':
        return False
    return True


def get_image_from_id(img_id: int) -> Union[bytes, Error]:
    """
    Accesses an external server and requests a picture with the specified id
    :param img_id: int, valid id of requested image
    :return: Union[bytes, Error], requested image in byte format or Error
    because of missing image with specified id
    """
    res = requests.get(f'{IMAGES_SERVER}/{img_id}')
    # OK
    if res.status_code == 200 or res.status_code // 100 == 2:
        return res.content
    # image not found
    elif res.status_code == 404:
        return Error(2)
    # image server problems
    elif res.status_code // 100 == 5:
        return Error(3)
    # problems with our access to server with images
    elif res.status_code // 100 == 4:
        return Error(4)
    # something other
    else:
        return Error(3, message='problems with server with images')


def read_plate_number(plate_reader: PlateReader,
                      img: bytes) -> Union[str, Error]:
    """
    Accepts an image with a car number as input and recognizes this number
    :param plate_reader: PlateReader, model to recognize a car number
    :param img: bytes, byte image with a car number
    :return: Union[str, Error], string with result of recognition or Error
    because of invalid image
    """
    # process bytes to image
    img = io.BytesIO(img)
    # send image to the model and get a number, if image is not valid -
    # return error
    try:
        res = plate_reader.read_text(img)
    except InvalidImage:
        return Error(1)
    return res


def process_image_id_to_plate_number(plate_reader: PlateReader,
                                     img_id: str) -> Union[str, Error]:
    """
    Accepts an image id as input, validate it, get image from external server,
    send it to the model and recognizes this number using plate reader model
    :param plate_reader: PlateReader, model to recognize a car number
    :param img_id: str, string will be validate for id
    :return: Union[str, Error], string with result of recognition or Error
    because of invalid image
    """
    # validate image id
    if not check_img_id_valid(img_id):
        return Error(5)
    # get image from external server in byte format, if get an error -
    # return it
    img_byte = get_image_from_id(img_id)
    if isinstance(img_byte, Error):
        return img_byte
    # recognizes a car number from image using plate reader model
    return read_plate_number(plate_reader, img_byte)


def result_json_handler(results: list[Any],
                        keys: list[Hashable]) -> Union[dict, Error]:
    """
    Returns an error if any of passed values is an error, otherwise returns
    the passed values in the dictionary with the passed keys
    :param results: list[Any], list of passed objects
    that will be the values in the returned dictionary
    :param keys: list[Hashable], a list of hashable objects
    that will be the keys in the returned dictionary
    :return: Union[str, Error], string with result of recognition or Error
    because of invalid image
    """
    # if the lengths of the lists of keys and values don't match,
    # issue a server error
    if len(results) != len(keys):
        return Error(7).return_error()
    errors_existence = [isinstance(res, Error) for res in results]
    # sequentially check all values, if there is at least one error -
    # log and return it
    if any(errors_existence):
        res = results[errors_existence.index(True)]
        logging.error(res.message)
        return res.return_error()
    # return dict with specified keys and values
    return {keys[i]: results[i] for i in range(len(keys))}

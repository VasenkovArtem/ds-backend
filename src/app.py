import logging
from flask import Flask, request
from models.plate_reader import PlateReader
from errors import Error
from utils import (read_plate_number, process_image_id_to_plate_number,
                   result_json_handler)


app = Flask(__name__)


@app.route('/')
def hello():
    if 'user' not in request.args:
        return '<h1 style="color:red;"><center>Hello user!</center></h1>'
    user = request.args['user']
    return f'<h1 style="color:red;"><center>Hello {user}!</center></h1>'


# <url>:8080 : body: {"user": "me"}
# -> {"result": "Hello me"}
@app.route('/greeting', methods=['POST'])
def greeting():
    if 'user' not in request.json:
        return Error(0, message='field "user" not found')
    user = request.json['user']
    return {'result': f'Hello {user}!'}


# <url>:8080/readPlateNumberFromImage : body <image bytes>
# {"plate_number": "c180mv ..."}
@app.route('/readPlateNumberFromImage', methods=['POST'])
def read_plate_number_from_image():
    """
    Read the car number from the picture transmitted in byte format
    using the POST method
    """
    # get data from request
    body = request.get_data()
    # check the data from the request for the required format
    if not isinstance(body, bytes):
        return Error(6).return_error()
    # send image to the model and get a number
    res = read_plate_number(plate_reader, body)
    # process the result and return it in the required format
    return result_json_handler([res], ['plate_number'])


# <url>:8080/readPlateNumberFromID?id=10022
# {"plate_number": "c180mv ..."}
@app.route('/readPlateNumberFromID')
def read_plate_number_from_id():
    """
    Read the car number from the image requested from the external server
    by its ID number received from the user using the GET method
    """
    # check for the required argument
    if 'id' not in request.args:
        return Error(0, message='field "id" not found').return_error()
    # get image id from request
    img_id = request.args['id']
    # validate image id, get image from server,
    # send it to the model and get a number
    res = process_image_id_to_plate_number(plate_reader, img_id)
    # process the result and return it in the required format
    return result_json_handler([res], ['plate_number'])


# <url>:8080/readPlateNumberFromIDs?id=10022&id=9965
# {"plate_number_1": "c180mv ...", "plate_number_2": "o156gh..."}
@app.route('/readPlateNumberFromIDs')
def read_plate_number_from_ids():
    """
    Read the car number from several images requested from an external server
    by their ID numbers received from the user using the GET method
    """
    # check for at less one of the required arguments
    if 'id' not in request.args:
        return Error(0, message='field "id" not found').return_error()
    # get image ids from request
    img_ids = request.args.getlist('id')
    results = []
    # process each image id, if get an error for at least one,
    # then return this error as a result
    for img_id in img_ids:
        # validate image id, get image from server,
        # send it to the model and get a number
        res = process_image_id_to_plate_number(plate_reader, img_id)
        # if get an error - return it
        if isinstance(res, Error):
            return res.return_error()
        results.append(res)
    num_imgs = len(img_ids)
    # process the result and return it in the required format
    return result_json_handler(results,
                               [f'plate_number_{i}' for i in range(num_imgs)])


if __name__ == '__main__':

    model_weights = r'./model_weights/plate_reader_model.pth'
    plate_reader = PlateReader.load_from_file(model_weights)

    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s] %(message)s',
        level=logging.INFO,
    )

    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=8080, debug=True)

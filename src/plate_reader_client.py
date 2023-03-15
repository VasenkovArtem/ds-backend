import requests


class PlateReaderClient:

    def __init__(self, host: str):
        self.host = host

    def read_plate_number_from_image(self, img: bytes) -> dict:
        """
        Sends the image sent by the user to the server
        and returns the result of plate recognition on it
        :param img: bytes, byte image with a car number
        :return: dict, server response result
        """
        res = requests.post(
            f'{self.host}/readPlateNumberFromImage',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=img,
        )
        return res.json()

    def read_plate_number_from_id(self, img_id: int) -> dict:
        """
        Sends the image id sent by the user to the server
        and returns the result of plate recognition on image with this id
        :param img_id: int, id of the image to be recognized
        :return: dict, server response result
        """
        res = requests.get(f'{self.host}/readPlateNumberFromID',
                           params={'id': img_id})
        return res.json()

    def read_plate_number_from_ids(self, img_ids: list) -> dict:
        """
        Sends the list of image ids sent by the user to the server
        and returns the results of plate recognition on images with this ids
        :param img_ids: list, id of the image to be recognized
        :return: dict, server response result
        """
        res = requests.get(f'{self.host}/readPlateNumberFromIDs',
                           params={'id': img_ids})
        return res.json()

    def greeting(self, user: str) -> dict:
        res = requests.post(
            f'{self.host}/readPlateNumber',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            json={
                'user': user,
            },
        )
        return res.json()


if __name__ == '__main__':
    client = PlateReaderClient(host='http://127.0.0.1:8080')
    with open('./images/9965.jpg', 'rb') as im:
        res = client.read_plate_number_from_image(im)
        print(res)
    print(client.read_plate_number_from_id(10022))
    print(client.read_plate_number_from_id(18))
    print(client.read_plate_number_from_ids([9965, 10022]))
    print(client.read_plate_number_from_ids(['1O8', '9965', '10022']))

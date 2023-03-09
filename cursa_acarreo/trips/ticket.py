from PIL import Image, ImageFont, ImageDraw
import qrcode
from cursa_acarreo import project_dir, formatdate_mx
import io, base64

'''
    This module includes the methods to create a custom ticket for trips.
    It takes a template image and add text and a QR code using PIL
'''


class Ticket:

    TICKET_TEMPLATE = project_dir + '/cursa_acarreo/static/print_templates/cursa_ticket_template.jpg'
    PUBLIC_TICKET_TEMPLATE = project_dir + '/cursa_acarreo/static/print_templates/cursa_public_ticket_template.jpg'
    TICKET_FONT = project_dir + '/cursa_acarreo/static/fonts/CalibriRegular.ttf'
    X_VALUE = 190  # X Coordinate to enter trip field text
    Y_VALUE_INIT = 295  # Initial Y coordinate for first trip value
    FIELD_INC = 115  # Increment of following fields position in case they are equally distributed
    TICKET_FIELDS = {'trip_id': (X_VALUE, Y_VALUE_INIT),
                     'truck': (X_VALUE, Y_VALUE_INIT + FIELD_INC),
                     'origin': (X_VALUE, Y_VALUE_INIT + 2*FIELD_INC),
                     'destination': (X_VALUE, Y_VALUE_INIT + 3*FIELD_INC),
                     'client': (X_VALUE, Y_VALUE_INIT + 3 * FIELD_INC),
                     'material': (X_VALUE, Y_VALUE_INIT + 4*FIELD_INC),
                     'amount': (X_VALUE, Y_VALUE_INIT + 5*FIELD_INC),
                     'sent_datetime': (X_VALUE, Y_VALUE_INIT + 6*FIELD_INC)}
    QR_XY = (175, 1080)  # Coordinates to paste QRcode

    def __init__(self, trip_dict):
        self.ticket_image = None
        self.ticket_fields_values = dict()
        self.ticket_fields_values['type'] = trip_dict['type']
        for i in self.TICKET_FIELDS:
            if trip_dict[i].__class__.__name__ == 'datetime':  # Convert datetime to formated string
                self.ticket_fields_values[i] = formatdate_mx(trip_dict[i])
            else:
                self.ticket_fields_values[i] = trip_dict[i]

    def __create_trip_qr(self):
        '''
        Creates a QR image with trip_id
        :return: PIL image object
        DOC: https://pypi.org/project/qrcode/
        '''
        qr = qrcode.QRCode(version=1, border=1, box_size=15)  # Size of image is controled by box_size
        qr.add_data(str(self.ticket_fields_values['trip_id']))
        qr.make(fit=True)
        qr_image = qr.make_image()
        return qr_image

    @staticmethod
    def format_value(text, line_length=23):
        '''
        Format String to max 2 lines no longer than 23 chars each line
        1.- Skip line at 23 chars, add a '-' if it is a work
        2.- Truncate at 23 on 2nd line and add "..."
        :param value:
        :return:
        '''
        text = str(text)
        ll = line_length  # Max Line Length
        if len(text) <= ll:  # Case 1
            return text
        elif ll < len(text) < 2*ll:
            if text[ll - 1] == ' ':  # Case 2A If last char of line is space no need to include '-'. just linebreak
                return text[0:ll] + '\n' + text[ll:]
            elif text[ll] == ' ':  # Case 2B If first char of new line is space, no need to include '-' and remove space
                return text[0:ll] + '\n' + text[ll + 1:]
            return text[0:ll - 1] + '-\n' + text[ll - 1:]  # Case 2C last char of line is a letter and word still continues un next line
        elif len(text) >= 2*line_length:
            if text[ll - 1] == ' ':  # Case 3A If last char of line is space no need to include '-'. just make the linebreak
                return text[0:ll] + '\n' + text[ll:2 * ll - 3] + '...'
            elif text[ll] == ' ':  # Case 3B If first char of new line is space, no need to include '-' and remove space
                return text[0:ll] + '\n' + text[ll + 1:2 * ll - 2] + '...'
            return text[0:ll - 1] + '-\n' + text[ll - 1:2 * ll - 3] + '...'  # Case 3C last char of line is a letter and word still continues un next line


    def create_ticket(self):
        '''
        Create ticket adding trip info and qrcode
        :return: PIL Image object
        '''
        if self.ticket_fields_values['type'] == 'internal' or not self.ticket_fields_values['type']:
            im = Image.open(self.TICKET_TEMPLATE)
        elif self.ticket_fields_values['type'] == 'public':
            im = Image.open(self.PUBLIC_TICKET_TEMPLATE)

        # Enter trip values
        fnt = ImageFont.truetype(self.TICKET_FONT, 45)  # Params = Font, Size
        d = ImageDraw.Draw(im)
        for f in self.TICKET_FIELDS:
            if ((self.ticket_fields_values['type'] == 'internal' or not self.ticket_fields_values['type']) and
                f == 'client') or \
                    (self.ticket_fields_values['type'] == 'public' and
                     (f in ['truck', 'destination'])):
                continue
            d.text(self.TICKET_FIELDS[f], self.format_value(self.ticket_fields_values[f]),
                   font=fnt, fill='black')

        # Generate and enter qr code
        if self.ticket_fields_values['type'] == 'internal' or not self.ticket_fields_values['type']:
            im.paste(self.__create_trip_qr(), self.QR_XY)
        self.ticket_image = im
        return self.ticket_image

# For future refactor. Apply design patters to make these methods apply only to created ticket:
    def save_ticket(self, filename):
        '''
        Save ticket image to specified filename. Full path must be specified
        :param filename:
        :return:
        '''
        if self.ticket_image:
            self.ticket_image.save(filename)
        else:
            raise ValueError('There is no ticket image created. First create image.')

    def encode_b64(self):
        '''
        Encode ticket to base64 string
        :return: String with base64 encoded image
        '''
        if self.ticket_image:
            imgByteArr = io.BytesIO()
            self.ticket_image.save(imgByteArr, format='JPEG')
            return base64.b64encode(imgByteArr.getvalue())
        else:
            raise ValueError('There is no ticket image created. First create image.')

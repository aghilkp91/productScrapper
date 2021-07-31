import requests
import logging
from apiclient import discovery
from googleapiclient.errors import HttpError
from oauth2client import file, client, tools
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
import oauth2client
import os.path
from mimetypes import MimeTypes
import httplib2

logger = logging.getLogger(__name__)

""" 
This is the class written for functions related to Image download and upload

We wanted to download the images of products and store in our databased with unique urls 
so that it can be used to plot in reports.

So this module contains the functions to download and upload images to google drive

"""

class Flag:
    auth_host_name = 'localhost'
    noauth_local_webserver = False
    auth_host_port = [8080, 8090]
    logging_level = 'ERROR'

try:
    flags = Flag()
except ImportError:
    flags = None

def get_credentials():
    """ 
    This funciton is to get the credentials for google drive

    Here we check if we already have a json file with the credentails
    stores. If not we generate new credentials and store it in the local.
    This will be reused till the session expires
    """
    home_dir = os.getcwd()
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        # if flags:
        credentials = tools.run_flow(flow, store, flags)
        # else:  # Needed only for compatibility with Python 2.6
        #     credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = os.path.dirname(os.path.realpath(__file__)) + '/client_secret.json'
APPLICATION_NAME = 'GDrive'
mime = MimeTypes()
credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
service = discovery.build('drive', 'v3', http=http)

class ImageUtils:
    """ 
    This Class contains the function for image downlaod (downloadImage) and image upload (uploadImage)

    All the images are stored to /spiders/temp folder in the local and deleted after uplaoding generally
    """
    main_upload_dir = "RevitImages"
    local_temp_folder = os.path.dirname(os.path.realpath(__file__)) + "/spiders/temp/"

    def uploadImage(self, file, file_ext):
        """ 
        This function uploads the image with given file extension to google drive and create an individual url
        which can be used to retrieve uniquely.

        :param file: Input Image path which needs to be  uplaoded
        :type file: str

        :param file_ext: Input Image extension to upload
        :type file_ext: str

        :return: return_url The unique image url which can use to access the image from google drive.
        :rtype: str 
        """
        file_metadata = {
            'name': file_ext,
            # 'mimeType' : 'application/vnd.google-apps.spreadsheet'
        }
        folder_list = service.files().list(q="mimeType = 'application/vnd.google-apps.folder'", fields="files(id,name)").execute()
        for folder in folder_list.get('files'):
            print('folder title: %s' % str(folder))
            if folder['name'] == self.main_upload_dir:
                folder_id = folder['id']
                break
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(file,
                                mimetype=mime.guess_type(os.path.basename(file))[0],
                                resumable=True)
        try:
            file = service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields='id').execute()
        except HttpError:
            print('corrupted file')
            pass
        return_url = 'https://drive.google.com/file/d/' + file.get('id')  + '/view'
        return return_url

    def downloadImage(self, image_url, file_path):
        """ 
        This function downlaods the image from the given image url with the name mentioned in filepath
        which can be used to retrieve uniquely.

        :param image_url: Input Image url which needs to be downloaded
        :type image_url: str

        :param file_path: Name to save the image
        :type file_path: str

        :return: return_url The local image path to which the image file is downlaoded.
        :rtype: str 
        """
        local_file_path = self.local_temp_folder + file_path
        img_data = requests.get(image_url).content
        with open(local_file_path, 'wb') as handler:
            handler.write(img_data)
        logger.debug('Image stored at %s' % local_file_path)
        return local_file_path

import logging
import requests
from numbers import Number
import xml.etree.cElementTree as xml
from urllib.parse import urlparse
from .exceptions import CouldNotDetermineProtocol, OperationFailed
from .checkers import check_tcp_udp_port_number
__author__ = 'Benjamin P. Trachtenberg'
__copyright__ = "Copyright (c) 2018, Benjamin P. Trachtenberg"
__credits__ = 'Benjamin P. Trachtenberg'
__license__ = 'MIT'
__status__ = 'prod'
__version_info__ = (1, 0, 2)
__version__ = '.'.join(map(str, __version_info__))
__maintainer__ = 'Benjamin P. Trachtenberg'
__email__ = 'e_ben_75-python@yahoo.com'
LOGGER = logging.getLogger(__name__)


class FileData(object):
    """
    Class to store a file info

    :type resource_url: String
    :param resource_url: The resource URL
    :type resource_name: String
    :param resource_name: The name of the resource
    :type file_size: String
    :param file_size: The file size
    :type modified_time: String
    :param modified_time: The modified date/time
    :type creation_time: String
    :param creation_time: The creation date/time
    :type content_type: String
    :param content_type: The content type

    """

    def __init__(self, resource_url, resource_name, file_size, modified_time, creation_time, content_type):
        self.resource_url = resource_url
        self.resource_name = resource_name
        self.file_size = file_size
        self.modified_time = modified_time
        self.creation_time = creation_time
        self.content_type = content_type

    def get_resource_url(self):
        """
        Method to get the WebDav resource url

        :rtype: String
        :return: A resource url

        """
        return self.resource_url

    def get_resource_name(self):
        """
        Method to get the WebDav resource name

        :rtype: String
        :return: A resource name

        """
        return self.resource_name

    def get_file_size(self):
        """
        Method to get the WebDav resource file size

        :rtype: String
        :return: A resource file size

        """
        return self.file_size

    def get_modified_time(self):
        """
        Method to get the WebDav resource modified date and time

        :rtype: String
        :return: A resource modified date and time

        """
        return self.modified_time

    def get_creation_time(self):
        """
        Method to get the WebDav resource creation date and time

        :rtype: String
        :return: A resource creation date and time

        """
        return self.creation_time

    def get_content_type(self):
        """
        Method to get the WebDav resource content type

        :rtype: String
        :return: A resource content type

        """
        return self.content_type

    def is_dir(self):
        """
        Method to check to see if WebDav resource is a directory

        :rtype: Boolean
        :return: True or False

        """
        if self.resource_url.endswith('/'):
            return True

        else:
            return False


class Client(object):
    """
    Class for WebDav Client

    :type host: String
    :param host: IP of the server
    :type port: Integer
    :param port: The TCT/UDP Port Number
    :type auth: String
    :param auth: Session auth
    :type username: String
    :param username: Username
    :type password: String
    :param password: Password
    :type protocol: String
    :param protocol: http, or https
    :type verify_ssl: Boolean
    :param verify_ssl: True or False
    :type path: String
    :param path: The path to the resource
    :type cert: String
    :param cert: Session cert

    :raises CouldNotDetermineProtocol: If protocol is not http or https

    """

    def __init__(self, host, port=None, auth=None, username=None, password=None,
                 protocol='http', verify_ssl=True, path=None, cert=None):
        if not port:
            if protocol == 'http':
                port = 80

            elif protocol == 'https':
                port = 443

            else:
                raise CouldNotDetermineProtocol('Class: {class_name} could not determine port for '
                                                '{protocol} port given was '
                                                '{port}'.format(class_name=type(self), protocol=protocol, port=port))

        check_tcp_udp_port_number(port)

        self.base_url = '{protocol}://{host}:{port}'.format(protocol=protocol, host=host, port=port)
        if path:
            self.base_url = '{base_url}/{path}'.format(base_url=self.base_url, path=path)

        self.current_working_directory = '/'
        self.session = requests.session()
        self.session.verify = verify_ssl
        self.session.stream = True

        if cert:
            self.session.cert = cert

        if auth:
            self.session.auth = auth

        elif username and password:
            self.session.auth = (username, password)

    def _send(self, method, path, expected_code, **kwargs):
        """
        Method to send data to WebDav server

        :type method:
        :param method: WebDav Method
        :type path: String
        :param path: WebDav Path to resource
        :type expected_code: Number
        :param expected_code: Expected HTTP Status Codes
        type kwargs: KWARGS
        :param kwargs: Key Word Arguments

        :rtype: requests.response Object
        :return: A response

        """
        url = self._get_url(path)
        response = self.session.request(method, url, allow_redirects=False, **kwargs)
        if isinstance(expected_code, Number) and response.status_code != expected_code\
                or not isinstance(expected_code, Number) and response.status_code not in expected_code:
            raise OperationFailed(method, path, expected_code, response.status_code)

        return response

    def _get_url(self, path):
        """
        Method used to get a good url

        :type path: String
        :param path: Path from the root directory

        :rtype: String
        :return: A good url

        """
        path = str(path).strip()
        if path.startswith('/'):
            return self.base_url + path

        return "".join((self.base_url, self.current_working_directory, path))

    def change_current_working_directory(self, path):
        """
        Method to change your current working directory

        :type path: String
        :param path: Path from your root

        :rtype: None
        :return: None

        """
        path = path.strip()
        if not path:
            return
        stripped_path = '/'.join(part for part in path.split('/') if part) + '/'
        if stripped_path == '/':
            self.current_working_directory = stripped_path

        elif path.startswith('/'):
            self.current_working_directory = '/' + stripped_path

        else:
            self.current_working_directory += stripped_path

    def directory_create(self, path, safe=False):
        """
        Method to make a directory

        :type path: String
        :param path: Path from your root
        :type safe: Boolean
        :param safe: If set to True it will silently do nothing is if directory already exists

        :rtype: None
        :return: None

        """
        expected_codes = 201 if not safe else (201, 301, 405)
        self._send('MKCOL', path, expected_codes)

    def directories_create(self, path):
        """
        Method to create nested directories

        :type path: String
        :param path: Path from your root

        :rtype: None
        :return: None

        """
        directories = [d for d in path.split('/') if d]
        if not directories:
            return

        if path.startswith('/'):
            directories[0] = '/' + directories[0]

        old_working_directory = self.current_working_directory
        try:
            for directory in directories:
                try:
                    self.directory_create(directory, safe=True)

                except OperationFailed as e:
                    if e.actual_code == 409:
                        raise

                finally:
                    self.change_current_working_directory(directory)

        finally:
            self.change_current_working_directory(old_working_directory)

    def directory_delete(self, path, safe=False):
        """
        Method to delete a directory

        :type path: String
        :param path: Path from your root
        :type safe: Boolean
        :param safe: If set to True it will silently do nothing is if directory already exists

        :rtype: None
        :return: None

        """
        path = str(path).rstrip('/') + '/'
        expected_codes = (200, 204) if not safe else (200, 204, 404)
        self._send('DELETE', path, expected_codes)

    def resource_delete(self, path):
        """
        Mwethod to delete a resource

        :type path: String
        :param path: Path from your root

        :rtype: None
        :return: None

        """
        expected_codes = (200, 204)
        self._send('DELETE', path, expected_codes)

    def upload(self, local_path_or_fileobj, remote_path):
        """
        Method to upload files to WebDav Server

        :type local_path_or_fileobj: String
        :param local_path_or_fileobj: The path
        :type remote_path: String
        :param remote_path: The path

        :rtype: None
        :return: None

        """
        expected_codes = (200, 201, 204)
        with open(local_path_or_fileobj, 'rb') as file:
            self._send('PUT', remote_path, expected_codes, data=file)

    def download(self, remote_path, local_path_or_fileobj):
        """
        Method to download files from WebDav server

        :type remote_path: String
        :param remote_path: The path
        :type local_path_or_fileobj: String
        :param local_path_or_fileobj: The path

        :rtype: None
        :return: None


        """
        download_chunk_size_bytes = 1 * 1024 * 1024
        expected_codes = 200
        response = self._send('GET', remote_path, expected_codes, stream=True)
        with open(local_path_or_fileobj, 'wb') as file:
            for chunk in response.iter_content(download_chunk_size_bytes):
                file.write(chunk)

    def resource_list(self, remote_path='.'):
        """
        Method to list resources on the WebDav server

        :type remote_path: String
        :param remote_path: The path

        :type: List
        :return: A list of FileData objects

        """
        headers = {'Depth': '1'}
        expected_codes = (207, 301)
        response = self._send('PROPFIND', remote_path, expected_codes, headers=headers)

        # Redirect
        if response.status_code == 301:
            url = urlparse(response.headers['location'])
            return self.resource_list(url.path)

        tree = xml.fromstring(response.content)
        return [self.__file_object_builder(element) for element in tree.findall('{DAV:}response')]

    def resource_exists(self, remote_path):
        """
        Method to verify if a resource exists on the WebDav server

        :type remote_path: String
        :param remote_path: The path

        :rtype: Boolean
        :return: True or False

        """
        expected_codes = (200, 301, 404)
        response = self._send('HEAD', remote_path, expected_codes)
        return True if response.status_code != 404 else False

    def get_current_working_directory(self):
        """
        Method to get current working directory

        :rtype: String
        :return: The current working directory

        """
        return self.current_working_directory

    def get_base_url(self):
        """
        Method to get base url

        :rtype: String
        :return: The base url

        """
        return self.base_url

    @staticmethod
    def get_xml_element(element, element_name, default=None):
        """
        Method to retrieve the data from the xml tree

        :type element: String
        :param element: The xml element
        :type element_name: String
        :param element_name: The property
        :type default: String
        :param default: What to set default to

        :rtype: String
        :return: A String

        """
        child = element.find('.//{DAV:}' + element_name)
        return default if child is None else child.text

    def __file_object_builder(self, element):
        """
        Method to build FileData objects

        :type element: String
        :param element: The xml element

        :rtype: FileData Object
        :return: A FileData object

        """
        return FileData(resource_url=self.get_xml_element(element, 'href'),
                        resource_name=self.get_xml_element(element, 'displayname'),
                        file_size=int(self.get_xml_element(element, 'getcontentlength', 0)),
                        modified_time=self.get_xml_element(element, 'getlastmodified', ''),
                        creation_time=self.get_xml_element(element, 'creationdate', ''),
                        content_type=self.get_xml_element(element, 'getcontenttype', ''))

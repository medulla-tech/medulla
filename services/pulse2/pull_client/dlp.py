import os
import stat
import shutil
import zipfile
import logging
import httplib
import urllib2
from base64 import b64encode

from config import PullClientConfig
from utils import get_hostname, get_mac_addresses
from http import HTTPClient, CookieSessionExpired


logger = logging.getLogger(__name__)


class DlpClient(HTTPClient):

    def __init__(self):
        self.config = PullClientConfig.instance()
        HTTPClient.__init__(self, self.config.Dlp.base_url, self.config.Service.name)
        if self.config.Dlp.hostname:
            self.hostname = self.config.Dlp.hostname
        else:
            self.hostname = get_hostname()
        if self.config.Dlp.mac_list:
            self.mac_list = self.config.Dlp.mac_list
        else:
            self.mac_list = get_mac_addresses()

    def auth(self):
        logger.debug("Authenticating against the DLP")
        try:
            res = self.post('auth', {'authkey': self.config.Dlp.authkey,
                                     'hostname': self.hostname,
                                     'mac_list': self.mac_list})
        except urllib2.URLError:
            logger.error("Failed to contact the DLP.")
        except CookieSessionExpired:
            logger.error("Can't establish the session cookie with the DLP. Check your time settings.")
        except httplib.InvalidURL as error:
            logger.error("DLP URL is invalid: %s" % error.message)
        else:
            if res.code == 200:
                return True
            elif res.code == 400:
                logger.error("Bad MAC addresses: %s" % self.mac_list)
            elif res.code == 401:
                logger.error("Bad DLP authkey")
            elif res.code == 404:
                logger.error("This machine is unknown to Pulse (%s, %s)" % (self.hostname, self.mac_list))
            elif res.code == 503:
                logger.error("Scheduler gone")
            else:
                logger.error("Failed to authenticate against the DLP (error %i)" % res.code)
        return False

    def get_commands(self):
        try:
            logger.debug("Get commands from DLP")
            res = self.get('commands')
        except urllib2.URLError:
            logger.error("Failed to contact the DLP.")
        except httplib.InvalidURL as error:
            logger.error("DLP URL is invalid: %s" % error.message)
        else:
            if res.code == 200:
                logger.debug("Result: %s" % res.data)
                return res.data
            elif res.code == 403 and self.auth():
                return self.get_commands()
            elif res.code == 503:
                logger.error("Package server gone")
            else:
                logger.error("Failed to get commands from the DLP (error %i)" % res.code)
        return []

    def clean_package(self, dir_path, zip_path):
        # Cleanup existing package
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        if os.path.exists(zip_path):
            os.unlink(zip_path)

    def get_package(self, uuid, workdir):
        """
        Get package uuid from the DLP in workdir

        The package is unzipped in a directory in the workdir
        The directory name is the package uuid
        """
        file = uuid + ".zip"
        dir_path = os.path.join(workdir, uuid)
        zip_path = os.path.join(workdir, file)
        self.clean_package(dir_path, zip_path)
        # Download file
        try:
            logger.debug("Downloading package %s" % file)
            res = self.get('file/%s' % file)
        except urllib2.URLError:
            logger.error("Failed to contact the DLP.")
        except httplib.InvalidURL as error:
            logger.error("DLP URL is invalid: %s" % error.message)
        else:
            if res.code == 200:
                f = open(zip_path, 'wb')
                f.write(res.data)
                f.close()
                # Extract zip file
                zip = zipfile.ZipFile(zip_path)
                zip.extractall(dir_path)
                # Remove downloaded zip
                #os.unlink(zip_path)
                # Fix permissions
                for file in os.listdir(dir_path):
                    os.chmod(os.path.join(dir_path, file), stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH)
                logger.debug("Package extracted at %s" % dir_path)
                return dir_path
            elif res.code == 401:
                logger.error("Not authorized to download %s" % file)
            elif res.code == 403 and self.get_commands():
                self.get_package(file, workdir)
            elif res.code == 404:
                logger.error("File %s not found" % file)
            else:
                logger.error("Failed to get package from the DLP (error: %i)" % res.code)
        return False

    def send_result(self, result):
        data = {'stdout': b64encode(result.stdout),
                'stderr': b64encode(result.stderr),
                'return_code': result.exitcode}
        try:
            logger.debug("Sending result %s to DLP" % result)
            res = self.post('step/%s/%s' % (result.command_id, result.step_name), data=data)
        except urllib2.URLError:
            logger.error("Failed to contact the DLP.")
        except httplib.InvalidURL as error:
            logger.error("DLP URL is invalid: %s" % error.message)
        else:
            if res.code == 201:
                return True
            if res.code == 400:
                logger.error("Malformed result")
            elif res.code == 401:
                logger.error("Not authorized")
            elif res.code == 403 and self.get_commands():
                self.send_result(result)
            elif res.code == 503:
                logger.error("Scheduler gone")
            else:
                logger.error("Failed to send result to the DLP (error: %i)" % res.code)
        return False

    def send_inventory(self, inventory):
        data = {'inventory': b64encode(inventory)}
        try:
            logger.debug("Sending inventory to DLP")
            res = self.post('inventory', data=data)
        except urllib2.URLError:
            logger.error("Failed to contact the DLP.")
        except httplib.InvalidURL as error:
            logger.error("DLP URL is invalid: %s" % error.message)
        else:
            if res.code == 201:
                return True
            elif res.code == 403 and self.auth():
                self.send_inventory(inventory)
            else:
                logger.error("Failed to send the inventory to the DLP (error: %i)" % res.code)
        return False


if __name__ == "__main__":
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    h = logging.StreamHandler()
    h.setFormatter(formatter)
    h.setLevel(logging.DEBUG)
    logger.addHandler(h)
    logger.setLevel(logging.DEBUG)

    client = DlpClient()
    client.get_commands()
    client.get_package("16e3d75a-3c5f-11e1-a659-0800271b75ea.zip", "/tmp")

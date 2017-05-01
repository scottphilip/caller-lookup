import sys
assert sys.version_info >= (2,7)

class C:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class CallerLookupInstall:

    LOCAL_FOLDER_PATH = "/var/lib/CallerLookup"
    GITHUB_MASTER_URL = 'https://raw.githubusercontent.com/scottphilip/caller-lookup/master'
    SUPERFECTA_SOURCES_PATH = '/var/www/html/admin/modules/superfecta/sources'
    ASTERISK_AGIBIN_PATH = '/var/lib/asterisk/agi-bin'
    INTERPRETER_PYTHON_PATH = "#!{0}".format(sys.executable)

    @staticmethod
    def Install_Package(package_name):
        CallerLookupInstall.Print_Update("Installing {0} ...".format(package_name))
        pip.main(['install', package_name])

    @staticmethod
    def Confirm(message):
        if CallerLookupInstall.Get_Input("{0} [Y/n]".format(message)).upper().startswith("Y"):
            return True
        return False

    @staticmethod
    def Get_Input(message):
        print("{0}{1}{2}\n".format(C.OKBLUE, message, C.ENDC))
        if sys.version_info >= 3:
            return raw_input()
        return input()

    @staticmethod
    def Print_Update(message):
        print("{0}{1}{2}\n".format(C.OKGREEN, message, C.ENDC))

    @staticmethod
    def Set_Interpreter(file_path):

        with open(file_path) as fin:
            lines = fin.readlines()
        lines[0] = CallerLookupInstall.INTERPRETER_PYTHON_PATH

        with open(file_path, 'w') as fout:
            for line in lines:
                fout.write(line)


if __name__ == "__main__":

    try:

        import os
        import sys
        import stat
        import pip
        import urllib

        os.makedirs(CallerLookupInstall.LOCAL_FOLDER_PATH)

        if CallerLookupInstall.Confirm("Do you want to save the Google Credentials in a configuration file?"):

            config_username = CallerLookupInstall.Get_Input("Please enter Google Account Username:")

            config_password = CallerLookupInstall.Get_Input("Please enter Google Account Password:")

            config_otpsecret = CallerLookupInstall.Get_Input("If enabled, enter the One Time Passcode Secret "
                                                             "(Leave blank if not enabled):")

            with open(CallerLookupInstall.LOCAL_FOLDER_PATH + "/CallerLookup.ini", "w+") as ini:
                ini.write("[Credentials]")
                ini.write("username = {0}".format(config_username))
                ini.write("password = {0}".format(config_password))
                ini.write("otpsecret = {0}".format(config_otpsecret))

        if CallerLookupInstall.Confirm("Do you want to install the required Python Packages?"):

            CallerLookupInstall.Install_Package("urllib")
            CallerLookupInstall.Install_Package("selenium")
            CallerLookupInstall.Install_Package("phonenumbers")
            CallerLookupInstall.Install_Package("pyotp")
            CallerLookupInstall.Install_Package("pyst2")
            CallerLookupInstall.Install_Package("configparser")
            CallerLookupInstall.Install_Package("http")
            CallerLookupInstall.Install_Package("cookiejar")
            CallerLookupInstall.Install_Package("parse")
            CallerLookupInstall.Install_Package("requests")

        CallerLookupInstall.Print_Update("Downloading CallerLookup Files ...")

        url = CallerLookupInstall.GITHUB_MASTER_URL + "/Python/CallerLookup.py"
        path = CallerLookupInstall.LOCAL_FOLDER_PATH + "/CallerLookup.py"
        urllib.urlretrieve(url, path)
        CallerLookupInstall.Set_Interpreter(path)
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IEXEC)

        if os.path.exists(CallerLookupInstall.ASTERISK_AGIBIN_PATH):
            url = CallerLookupInstall.GITHUB_MASTER_URL + "/Plugins/AsteriskAGI-SetCIDName.py"
            path = CallerLookupInstall.ASTERISK_AGIBIN_PATH + "/AsteriskAGI-SetCIDName.py"
            urllib.urlretrieve(url, path)
            CallerLookupInstall.Set_Interpreter(path)
            st = os.stat(path)
            os.chmod(path, st.st_mode | stat.S_IEXEC)

        if os.path.exists(CallerLookupInstall.SUPERFECTA_SOURCES_PATH):
            url = CallerLookupInstall.GITHUB_MASTER_URL + "/Plugins/source-CallerLookup.module.php"
            path = CallerLookupInstall.SUPERFECTA_SOURCES_PATH + "/sources-CallerLookup.module"
            urllib.urlretrieve(url, path)

        CallerLookupInstall.Print_Update("Complete.")
        exit(0)

    except Exception as e:

        print("{0}An error has occurred during setup.{1}{2}".format(C.FAIL, str(e), C.ENDC))
        exit(1)


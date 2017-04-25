#!/bin/bash

if [ "$EUID" -ne 0 ]
then
    echo "Usage: sudo wget ..."
    exit;
fi

echo_header()
{
    reset
    echo "=================================================================="
    echo "=               CallerLookup Install (CentOS)                    ="
    echo "=================================================================="
}

install()
{
    $is_python3 = $false
    $is_pip = $false
    $is_selenium = $false
    $is_phonenumbers = $false

    if command -v python3 > /dev/null 2>&1; then
        $is_python3 = $true
        if command -v pip > /dev/null 2>&1; then
            $$is_pip = $true
        fi
        if [$is_pip == $true]
        then
            $is_selenium = "$($(len$(pip show selenium) > 0))" || $false;
            $is_phonenumbers = "$($(len$(pip show phonenumbers) > 0))" || $false;
        fi
    fi

    if [$is_python3 || $is_pip || $is_selenium || $is_phonenumbers];
    then
        echo_header
        echo "The following dependencies will be installed:"
        if [$is_python3]; then echo "       - Python3 (Yum)"; fi
        if [is_pip]; then echo "         - PIP  (Yum)"; fi
        if [is_selenium]; then echo "           - Selenium (PIP)"; fi
        if [is_phonenumbers]; then echo "           - PhoneNumbers (PIP)"; fi
        echo "Are you sure you want to install these dependencies? [Y/N]"

        read $install_confirm
        case ${install_confirm:0:1} in
            y|Y )

                echo_header

                if [!$is_python3];
                then
                    printf "\rInstalling Python3 ... "
                    unbuffer yum install python3 > python3_log
                    echo "Installing Python3 ... done"
                fi

                if [!$is_pip];
                then
                    printf "\rInstalling PIP ... "
                    unbuffer yum install python-pip python-wheel > pip_log
                    unbuffer yum upgrade python-setuptools > pipsetuptools_log
                    echo "Installing PIP ... done"
                fi

                if [!$is_selenium];
                then
                    printf "\rInstalling Selenium ... "
                    unbuffer pip install selenium > selenium_log
                    echo "Installing Selenium ... done"
                fi

                if [!$is_phonenumbers];
                then
                    printf "\rInstalling PhoneNumbers ... "
                    unbuffer pip install phonenumbers > phonenumbers_log
                    echo "Installing PhoneNumbers ... done"
                fi
            ;;
            * )
                exit
            ;;
        esac
    fi

    # Asterisk AGI
    if [ -d "/var/lib/asterisk/agi-bin" ]; then
        printf "\rInstalling Asterisk AGI Script ... "
        unbuffer wget  -O /var/lib/asterisk/agi-bin/AgiCallerLookup.py "https://raw.githubusercontent.com/scottphilip/caller-lookup/master/Plugins/AgiCallerLookup.py" > agi_log
        chmod +x /var/lib/asterisk/agi-bin/AgiCallerLookup.py
        echo "Installing Asterisk AGI Script ... done"
    fi

    # FreeBPX - Superfecta
    if [ -d "/var/www/html/admin/modules/superfecta/sources/" ]; then
        printf "\rInstalling FreePBX Superfecta Source ... "
        unbuffer wget  -O /var/www/html/admin/modules/superfecta/sources/source-CallerLookup.module "https://raw.githubusercontent.com/scottphilip/caller-lookup/master/Plugins/source-CallerLookup.module.php" > superfecta_log
        echo "Installing FreePBX Superfecta Source ... done"
    fi

    echo "Install Complete"
    exit

}

install
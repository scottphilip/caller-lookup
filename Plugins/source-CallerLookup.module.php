/*
    /var/www/html/admin/modules/superfecta/sources/source-CallerLookup.module
*/
<?php

class DatabaseAction extends Thread
{
    public function __construct($db, $key, $value)
    {
        $this->db = $db;
        $this->key = $key;
        $this->value = $value;
    }

    function run()
    {
        global $amp_conf;
        global $astman;

        if ($astman)
        {
            if (!$astman->database_get($this->db,$this->key))
            {
                $astman->database_put($this->db,$this->key, $this->value);
            }
        }
        else
        {
            fatal("Cannot connect to Asterisk Manager with ".$amp_conf["AMPMGRUSER"]."/".$amp_conf["AMPMGRPASS"]);
        }
    }
}

class CallerLookup extends superfecta_base
{
    private $country_codes_path = "/var/lib/CallerLookup/CountryCodes.json"

    function get_country_codes($is_display)
    {
        $data = json_decode(file_get_contents($country_codes_path), true));
        $result = array();
        $current_index = 1;
        foreach($data as $key => $value)
        {
            if ($is_display)
            {
                array_push($result, sprintf("%s (+%s)", $value=>CN, $value=>CC));
            }
            else
            {
                array_push($result, strtoupper($value=>CCN));
            }
        }
        return $result
    }
    public $description = "CallerLookup (TrueCaller)";
    public $version_requirement = "2.11";
    public $source_param = array(
        'AccountInfo' => array(
          'description' => "Google Account Credentials (Two factor authentication must be disabled):",
          'type' => 'info'
        ),
        'Username' => array(
          'description' => "Email",
          'type' => 'text'
        ),
        'Password' => array(
          'description' => "Password",
          'type' => 'password'
        ),
        'OTPSecret' => array(
          'description' => "2-Factor Login Secret",
          'type' => 'text'
        ),
        'Default_Region' => array(
          'description' => "Default Country CCN",
          'type' => 'select',
          'option' => get_country_codes(true),
          'default' => array_search('DE', get_country_codes(false))
        ),
        'ScoreInfo' => array(
          'description' => "Each identified number has a score associated.  The higher the score, the less likely it is a Spam call.",
          'type' => 'info'
        ),
        'Spam_Threshold' => array(
        'description' => "Mark calls as Spam if their score is below:",
        'type' => 'select',
        'option' => array(
                1 => "Never",
                2 => "1",
                3 => "2",
                4 => "3 (Recommended)",
                5 => "4",
                6 => "5",
                7 => "6",
                8 => "7",
                9 => "8",
                10 => "9"
            ),
            'default' => '4'
        ),
        'Add_Phonebook' => array(
          'description' => "Add Names to Phonebook? (When not marked as Spam)",
          'type' => 'checkbox',
          'default' => 'false'
        ),
        'Add_Blacklist' => array(
          'description' => "Add Spam Calls to Blacklist?",
          'type' => 'checkbox',
          'default' => 'false'
        )
    );

    function get_caller_id($thenumber, $run_param=array())
    {
        $this->spam = false;
        $is_debug = $this->debug;
        $result_name = NULL;

        $username = $run_param['Username'];
        $password = $run_param['Password'];
        $otpsecret = $run_param['OTPSecret'];

        $spam_threshold = $run_param['Spam_Threshold'] == 1 ? 0 : $run_param['Spam_Threshold'] - 1;
        $is_add_phonebook = $run_param['Add_Phonebook'];
        $is_add_blacklist = $run_param['Add_Blacklist'];
        $default_region = get_country_codes(false)[$run_param['Default_Region']];

        $this->DebugPrint(sprintf("CallerLookup: Username -> %s", $username));
        $this->DebugPrint(sprintf("CallerLookup: Default Region -> %s", $default_region));
        $this->DebugPrint(sprintf("CallerLookup: Threshold -> %s", $spam_threshold));
        $this->DebugPrint(sprintf("CallerLookup: Add To Phonebook? -> %s", $is_add_phonebook?"Yes":"No"));
        $this->DebugPrint(sprintf("CallerLookup: Add To Blacklist? -> %s", $is_add_blacklist?"Yes":"No"));

        $script_path = '/var/lib/CallerLookup/CallerLookup.py'

        $credentials = ""
        if (len($username) > 0)
        {
            $credentials = sprintf(" --username %s --password %s --otpsecret %s", $username, $password, $otpsecret)
        }

        $command = sprintf("python3 %s --number %s --region %s%s%s",
                        $script_path,
                        $thenumber,
                        $default_region,
                        $credentials
                        $is_debug ? " --debug" : "")
        $this->DebugPrint(sprintf("CallerLookup: Command -> %s", $command));

        try
        {
            exec($command, $output, $return_var);
            $this->DebugPrint(sprintf("CallerLookup: Result Code -> %s", $return_var));
            $this->DebugPrint(sprintf("CallerLookup: Result Output -> %s", $output));
        }
        catch (Exception $e)
        {
            $this->DebugPrint(sprintf("CallerLookup: Execution Error -> %s", $e->getMessage()));
        }

        if ($return_var == 0)
        {
            $result = json_decode($output, true);

            if (len($result) > 0)
            {
                $result = $result[0]

                if (isset($result['Result']) && $result['Result'] == "success")
                {
                    if (isset($result['Score']) && $result['Score'] >= 0)
                    {
                        if (($result['Score'] * 10) < $spam_threshold)
                        {
                            $this->spam = true;
                        }
                    }

                    if (issset($result['Name']) && len($result['Name']) > 0)
                    {
                        $result_name = $result['Name'];
                    }

                    if ($this->spam)
                    {
                        if ($is_add_blacklist)
                        {
                            if (is_null($result_name))
                            {
                                $result_name = "SPAM";
                            }
                            $this->DebugPrint("CallerLookup: Blacklist - $result_name ($thenumber)");
                            $bl_thread = new DatabaseAction('blacklist', trim($thenumber), trim($result_name));
                            $bl_thread.start();
                        }
                    }
                    else
                    {
                        if ($is_add_phonebook && !is_null($result_name))
                        {
                            $this->DebugPrint("CallerLookup: Phonebook - $result_name ($thenumber)");
                            $bl_thread = new DatabaseAction('cidname', trim($thenumber), trim($result_name));
                            $bl_thread.start();
                        }
                    }
                }
            }
        }
        return is_null($result_name) ? "" : $result_name;
    }
}

?>
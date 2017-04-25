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
            if (!$astman->database_get($this->db,$this->key)) {
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
    'Default_Region' => array(
      'description' => "Default Country CCN",
      'type' => 'text',
      'default' => 'GB'
    ),
    'Spam_Threshold' => array(
      'description' => "Minimum Score (0 - 10)",
      'type' => 'number',
      'default' => '1'
    ),
    'Add_Phonebook' => array(
      'description' => "Add to Phonebook?",
      'type' => 'checkbox',
      'default' => 'true'
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
    $spam_threshold = isset($run_param['Spam_Threshold']) ? $run_param['Spam_Threshold'] : 0;
    $is_add_phonebook = $run_param['Add_Phonebook'];
    $is_add_blacklist = $run_param['Add_Blacklist'];
    $default_region = $run_param['Default_Region'];

    $this->DebugPrint(sprintf("CallerLookup: Username -> %s", $username));
    $this->DebugPrint(sprintf("CallerLookup: Default Region -> %s", $default_region));
    $this->DebugPrint(sprintf("CallerLookup: Threshold -> %s", $spam_threshold));
    $this->DebugPrint(sprintf("CallerLookup: Add To Phonebook? -> %s", $is_add_phonebook?"Yes":"No"));
    $this->DebugPrint(sprintf("CallerLookup: Add To Blacklist? -> %s", $is_add_blacklist?"Yes":"No"));

    //TODO: Path
    $script_path = '/usr/bin/CallerLookup.py'

    $command = sprintf("python %s --number %s --region %s --username %s --password %s %s",
                    $script_path,
                    $thenumber,
                    $default_region,
                    $is_debug?"--debug":"")
    $this->DebugPrint(sprintf("CallerLookup: Command -> %s", $command));

    exec($command, $output, $return_var);
    $this->DebugPrint(sprintf("CallerLookup: Result Code -> %s", $return_var));

    if ($return_var == 0)
    {

        $this->DebugPrint(sprintf("CallerLookup: Result Data -> %s", $output));
        $result = json_decode($output, true);

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


                if ($is_add_blacklist) {

                    if (is_null($result_name)) {
                        $result_name = "SPAM";
                    }

                    $this->DebugPrint("CallerLookup: Blacklist - $result_name ($thenumber)");
                    $bl_thread = new DatabaseAction('blacklist', trim($thenumber), trim($result_name));
                    $bl_thread.start();

                }
            }
            else
            {

                if ($is_add_phonebook && !is_null($result_name)) {

                    $this->DebugPrint("CallerLookup: Phonebook - $result_name ($thenumber)");
                    $bl_thread = new DatabaseAction('cidname', trim($thenumber), trim($result_name));
                    $bl_thread.start();

                }
            }
        }
    }

	return is_null($result_name) ? "" : $result_name;
  }
}

?>
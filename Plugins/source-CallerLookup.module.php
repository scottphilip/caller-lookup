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

    private $ccn_codes = array(
        1 => "AF",
        2 => "AL",
        3 => "DZ",
        4 => "AS",
        5 => "AD",
        6 => "AO",
        7 => "AI",
        8 => "AG",
        9 => "AR",
        10 => "AM",
        11 => "AW",
        12 => "AU",
        13 => "AT",
        14 => "AZ",
        15 => "BS",
        16 => "BH",
        17 => "BD",
        18 => "BB",
        19 => "BY",
        20 => "BE",
        21 => "BZ",
        22 => "BJ",
        23 => "BM",
        24 => "BT",
        25 => "BO",
        26 => "BA",
        27 => "BW",
        28 => "BR",
        29 => "IO",
        30 => "VG",
        31 => "BN",
        32 => "BG",
        33 => "BF",
        34 => "MM",
        35 => "BI",
        36 => "KH",
        37 => "CM",
        38 => "CA",
        39 => "CV",
        40 => "KY",
        41 => "CF",
        42 => "TD",
        43 => "CL",
        44 => "CN",
        45 => "CX",
        46 => "CO",
        47 => "KM",
        48 => "CG",
        49 => "CD",
        50 => "CK",
        51 => "CR",
        52 => "HR",
        53 => "CU",
        54 => "CY",
        55 => "CZ",
        56 => "DK",
        57 => "DJ",
        58 => "DM",
        59 => "DO",
        60 => "DO",
        61 => "DO",
        62 => "TL",
        63 => "EC",
        64 => "EG",
        65 => "SV",
        66 => "GQ",
        67 => "ER",
        68 => "EE",
        69 => "ET",
        70 => "FO",
        71 => "FJ",
        72 => "FI",
        73 => "FR",
        74 => "GF",
        75 => "PF",
        76 => "GA",
        77 => "GM",
        78 => "GE",
        79 => "DE",
        80 => "GH",
        81 => "GI",
        82 => "GR",
        83 => "GL",
        84 => "GD",
        85 => "GP",
        86 => "GU",
        87 => "GT",
        88 => "GN",
        89 => "GW",
        90 => "GY",
        91 => "HT",
        92 => "HN",
        93 => "HK",
        94 => "HU",
        95 => "IS",
        96 => "IN",
        97 => "ID",
        98 => "IR",
        99 => "IQ",
        100 => "IE",
        101 => "IL",
        102 => "IT",
        103 => "CI",
        104 => "JM",
        105 => "JP",
        106 => "JO",
        107 => "KZ",
        108 => "KE",
        109 => "KI",
        110 => "KW",
        111 => "KG",
        112 => "LA",
        113 => "LV",
        114 => "LB",
        115 => "LS",
        116 => "LR",
        117 => "LY",
        118 => "LI",
        119 => "LT",
        120 => "LU",
        121 => "MO",
        122 => "MK",
        123 => "MG",
        124 => "MW",
        125 => "MY",
        126 => "MV",
        127 => "ML",
        128 => "MT",
        129 => "MH",
        130 => "MQ",
        131 => "MR",
        132 => "MU",
        133 => "YT",
        134 => "MX",
        135 => "MD",
        136 => "MC",
        137 => "MN",
        138 => "ME",
        139 => "MS",
        140 => "MA",
        141 => "MZ",
        142 => "NA",
        143 => "NR",
        144 => "NP",
        145 => "NL",
        146 => "CW",
        147 => "NC",
        148 => "NZ",
        149 => "NI",
        150 => "NE",
        151 => "NG",
        152 => "NU",
        153 => "NF",
        154 => "MP",
        155 => "KP",
        156 => "NO",
        157 => "OM",
        158 => "PK",
        159 => "PW",
        160 => "PS",
        161 => "PA",
        162 => "PG",
        163 => "PY",
        164 => "PE",
        165 => "PH",
        166 => "PN",
        167 => "PL",
        168 => "PT",
        169 => "PR",
        170 => "QA",
        171 => "RE",
        172 => "RO",
        173 => "RU",
        174 => "RW",
        175 => "SH",
        176 => "KN",
        177 => "LC",
        178 => "MF",
        179 => "PM",
        180 => "VC",
        181 => "WS",
        182 => "SM",
        183 => "ST",
        184 => "SA",
        185 => "SN",
        186 => "RS",
        187 => "SC",
        188 => "FK",
        189 => "SL",
        190 => "SG",
        191 => "SK",
        192 => "SI",
        193 => "SB",
        194 => "SO",
        195 => "ZA",
        196 => "KR",
        197 => "SS",
        198 => "ES",
        199 => "LK",
        200 => "SD",
        201 => "SR",
        202 => "SZ",
        203 => "SE",
        204 => "CH",
        205 => "SY",
        206 => "TW",
        207 => "TJ",
        208 => "TZ",
        209 => "TH",
        210 => "TG",
        211 => "TK",
        212 => "TO",
        213 => "TT",
        214 => "TN",
        215 => "TR",
        216 => "TM",
        217 => "TC",
        218 => "TV",
        219 => "UG",
        220 => "GB",
        221 => "UA",
        222 => "AE",
        223 => "UY",
        224 => "US",
        225 => "UZ",
        226 => "VU",
        227 => "VE",
        228 => "VN",
        229 => "VI",
        230 => "WF",
        231 => "YE",
        232 => "ZM",
        233 => "ZW");
    private $cn_codes = array(
        1 => "Afghanistan (+93)",
        2 => "Albania (+355)",
        3 => "Algeria (+213)",
        4 => "American Samoa (+1684)",
        5 => "Andorra (+376)",
        6 => "Angola (+244)",
        7 => "Anguilla (+1264)",
        8 => "Antigua and Barbuda (+1268)",
        9 => "Argentina (+54)",
        10 => "Armenia (+374)",
        11 => "Aruba (+297)",
        12 => "Australia (+61)",
        13 => "Austria (+43)",
        14 => "Azerbaijan (+994)",
        15 => "Bahamas (+1242)",
        16 => "Bahrain (+973)",
        17 => "Bangladesh (+880)",
        18 => "Barbados (+1246)",
        19 => "Belarus (+375)",
        20 => "Belgium (+32)",
        21 => "Belize (+501)",
        22 => "Benin (+229)",
        23 => "Bermuda (+1441)",
        24 => "Bhutan (+975)",
        25 => "Bolivia (+591)",
        26 => "Bosnia and Herzegovina (+387)",
        27 => "Botswana (+267)",
        28 => "Brazil (+55)",
        29 => "British Indian Ocean Territory (+246)",
        30 => "British Virgin Islands (+1284)",
        31 => "Brunei (+673)",
        32 => "Bulgaria (+359)",
        33 => "Burkina Faso (+226)",
        34 => "Burma-Myanmar (+95)",
        35 => "Burundi (+257)",
        36 => "Cambodia (+855)",
        37 => "Cameroon (+237)",
        38 => "Canada (+1)",
        39 => "Cape Verde (+238)",
        40 => "Cayman Islands (+1345)",
        41 => "Central African Republic (+236)",
        42 => "Chad (+235)",
        43 => "Chile (+56)",
        44 => "China (+86)",
        45 => "Christmas Island (+6189)",
        46 => "Colombia (+57)",
        47 => "Comoros (+269)",
        48 => "Congo (+242)",
        49 => "Congo The Democratic Republic (+243)",
        50 => "Cook Islands (+682)",
        51 => "Costa Rica (+506)",
        52 => "Croatia (+385)",
        53 => "Cuba (+53)",
        54 => "Cyprus (+357)",
        55 => "Czech Republic (+420)",
        56 => "Denmark (+45)",
        57 => "Djibouti (+253)",
        58 => "Dominica (+1767)",
        59 => "Dominican Republic (+1849)",
        60 => "Dominican Republic (+1829)",
        61 => "Dominican Republic (+1809)",
        62 => "East Timor (+670)",
        63 => "Ecuador (+593)",
        64 => "Egypt (+20)",
        65 => "El Salvador (+503)",
        66 => "Equatorial Guinea (+240)",
        67 => "Eritrea (+291)",
        68 => "Estonia (+372)",
        69 => "Ethiopia (+251)",
        70 => "Faroe Islands (+298)",
        71 => "Fiji (+679)",
        72 => "Finland (+358)",
        73 => "France (+33)",
        74 => "French Guiana (+594)",
        75 => "French Polynesia (+689)",
        76 => "Gabon (+241)",
        77 => "Gambia (+220)",
        78 => "Georgia (+995)",
        79 => "Germany (+49)",
        80 => "Ghana (+233)",
        81 => "Gibraltar (+350)",
        82 => "Greece (+30)",
        83 => "Greenland (+299)",
        84 => "Grenada (+1473)",
        85 => "Guadeloupe (+590)",
        86 => "Guam (+1671)",
        87 => "Guatemala (+502)",
        88 => "Guinea (+224)",
        89 => "Guinea-Bissau (+245)",
        90 => "Guyana (+592)",
        91 => "Haiti (+509)",
        92 => "Honduras (+504)",
        93 => "Hong Kong (+852)",
        94 => "Hungary (+36)",
        95 => "Iceland (+354)",
        96 => "India (+91)",
        97 => "Indonesia (+62)",
        98 => "Iran (+98)",
        99 => "Iraq (+964)",
        100 => "Ireland (+353)",
        101 => "Israel (+972)",
        102 => "Italy (+39)",
        103 => "Ivory Coast (+225)",
        104 => "Jamaica (+1876)",
        105 => "Japan (+81)",
        106 => "Jordan (+962)",
        107 => "Kazakhstan (+7)",
        108 => "Kenya (+254)",
        109 => "Kiribati (+686)",
        110 => "Kuwait (+965)",
        111 => "Kyrgyzstan (+996)",
        112 => "Laos (+856)",
        113 => "Latvia (+371)",
        114 => "Lebanon (+961)",
        115 => "Lesotho (+266)",
        116 => "Liberia (+231)",
        117 => "Libya (+218)",
        118 => "Liechtenstein (+423)",
        119 => "Lithuania (+370)",
        120 => "Luxembourg (+352)",
        121 => "Macau (+853)",
        122 => "Macedonia (+389)",
        123 => "Madagascar (+261)",
        124 => "Malawi (+265)",
        125 => "Malaysia (+60)",
        126 => "Maldives (+960)",
        127 => "Mali (+223)",
        128 => "Malta (+356)",
        129 => "Marshall Islands (+692)",
        130 => "Martinique (+596)",
        131 => "Mauritania (+222)",
        132 => "Mauritius (+230)",
        133 => "Mayotte (+262)",
        134 => "Mexico (+52)",
        135 => "Moldova (+373)",
        136 => "Monaco (+377)",
        137 => "Mongolia (+976)",
        138 => "Montenegro (+382)",
        139 => "Montserrat (+1664)",
        140 => "Morocco (+212)",
        141 => "Mozambique (+258)",
        142 => "Namibia (+264)",
        143 => "Nauru (+674)",
        144 => "Nepal (+977)",
        145 => "Netherlands (+31)",
        146 => "CuraÃ§ao (+599)",
        147 => "New Caledonia (+687)",
        148 => "New Zealand (+64)",
        149 => "Nicaragua (+505)",
        150 => "Niger (+227)",
        151 => "Nigeria (+234)",
        152 => "Niue (+683)",
        153 => "Norfolk Island (+672)",
        154 => "Northern Mariana Islands (+1670)",
        155 => "North Korea (+850)",
        156 => "Norway (+47)",
        157 => "Oman (+968)",
        158 => "Pakistan (+92)",
        159 => "Palau (+680)",
        160 => "Palestine (+970)",
        161 => "Panama (+507)",
        162 => "Papua New Guinea (+675)",
        163 => "Paraguay (+595)",
        164 => "Peru (+51)",
        165 => "Philippines (+63)",
        166 => "Pitcairn Islands (+870)",
        167 => "Poland (+48)",
        168 => "Portugal (+351)",
        169 => "Puerto Rico (+1787)",
        170 => "Qatar (+974)",
        171 => "RÃ©union (+262)",
        172 => "Romania (+40)",
        173 => "Russia (+7)",
        174 => "Rwanda (+250)",
        175 => "Saint Helena (+290)",
        176 => "Saint Kitts and Nevis (+1869)",
        177 => "Saint Lucia (+1758)",
        178 => "Saint Martin (+1599)",
        179 => "Saint Pierre and Miquelon (+508)",
        180 => "Saint Vincent and the Grenadines (+1784)",
        181 => "Samoa (+685)",
        182 => "San Marino (+378)",
        183 => "SÃ£o TomÃ© and PrÃ­ncipe (+239)",
        184 => "Saudi Arabia (+966)",
        185 => "Senegal (+221)",
        186 => "Serbia (+381)",
        187 => "Seychelles (+248)",
        188 => "Falkland Islands (+500)",
        189 => "Sierra Leone (+232)",
        190 => "Singapore (+65)",
        191 => "Slovakia (+421)",
        192 => "Slovenia (+386)",
        193 => "Solomon Islands (+677)",
        194 => "Somalia (+252)",
        195 => "South Africa (+27)",
        196 => "South Korea (+82)",
        197 => "South Sudan (+211)",
        198 => "Spain (+34)",
        199 => "Sri Lanka (+94)",
        200 => "Sudan (+249)",
        201 => "Suriname (+597)",
        202 => "Swaziland (+268)",
        203 => "Sweden (+46)",
        204 => "Switzerland (+41)",
        205 => "Syria (+963)",
        206 => "Taiwan (+886)",
        207 => "Tajikistan (+992)",
        208 => "Tanzania (+255)",
        209 => "Thailand (+66)",
        210 => "Togo (+228)",
        211 => "Tokelau (+690)",
        212 => "Tonga (+676)",
        213 => "Trinidad and Tobago (+1868)",
        214 => "Tunisia (+216)",
        215 => "Turkey (+90)",
        216 => "Turkmenistan (+993)",
        217 => "Turks and Caicos Islands (+1649)",
        218 => "Tuvalu (+688)",
        219 => "Uganda (+256)",
        220 => "United Kingdom (+44)",
        221 => "Ukraine (+380)",
        222 => "United Arab Emirates (+971)",
        223 => "Uruguay (+598)",
        224 => "United States (+1)",
        225 => "Uzbekistan (+998)",
        226 => "Vanuatu (+678)",
        227 => "Venezuela (+58)",
        228 => "Vietnam (+84)",
        229 => "Virgin Islands (+1340)",
        230 => "Wallis and Futuna (+681)",
        231 => "Yemen (+967)",
        232 => "Zambia (+260)",
        233 => "Zimbabwe (+263)");

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
          'option' => $cn_codes,
          'default' => 'DE'
        ),
        'ScoreInfo' => array(
          'description' => "Each identified number has a score associated.  The higher the score, the least likely it is a Spam call.  ",
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
          'description' => "Add Names to Phonebook?",
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
        $otpsecret = $run_param['OTPSecret'];

        $spam_threshold = $run_param['Spam_Threshold'] == 1 ? 0 : $run_param['Spam_Threshold'] - 1;
        $is_add_phonebook = $run_param['Add_Phonebook'];
        $is_add_blacklist = $run_param['Add_Blacklist'];
        $default_region = $ccn_codes[$run_param['Default_Region']];

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

        $command = sprintf("python %s --number %s --region %s%s%s",
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
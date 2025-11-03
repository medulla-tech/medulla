<?php
/*
 * (c) 2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
// -----
// DATAS for form
// -----

$info_comment_this_field = _T("Check to uncomment this field", "imaging");
$info_installation_note = _T("Meta Information config", "imaging");
// ---- locale

$info_locale_settings = _T("Preseeding only locale sets language, country and locale.", "imaging");
$locales_country = [
    "United States",
    "United Kingdom",
    "France",
    "Canada",
    "Germany",
    "Spain",
    "Portugal",
    "Brazil",
    "Italy",
    "Netherlands",
    "Denmark",
    "Finland",
    "Norway",
    "Sweden",
    "Russia",
    "Poland",
    "Czech Republic",
    "Hungary",
    "Turkey",
    "Greece",
    "Egypt",
    "Israel",
    "Japan",
    "South Korea",
    "China",
    "Taiwan",
    "India",
];

$locales_values= [
    "en_US.UTF-8",
    "en_GB.UTF-8",
    "fr_FR.UTF-8",
    "fr_CA.UTF-8",
    "de_DE.UTF-8",
    "es_ES.UTF-8",
    "pt_PT.UTF-8",
    "pt_BR.UTF-8",
    "it_IT.UTF-8",
    "nl_NL.UTF-8",
    "da_DK.UTF-8",
    "fi_FI.UTF-8",
    "nb_NO.UTF-8",
    "sv_SE.UTF-8",
    "ru_RU.UTF-8",
    "pl_PL.UTF-8",
    "cs_CZ.UTF-8",
    "hu_HU.UTF-8",
    "tr_TR.UTF-8",
    "el_GR.UTF-8",
    "ar_EG.UTF-8",
    "he_IL.UTF-8",
    "ja_JP.UTF-8",
    "ko_KR.UTF-8",
    "zh_CN.UTF-8",
    "zh_TW.UTF-8",
    "hi_IN.UTF-8",
];

$languages_values = [
    "aa",
    "af",
    "am",
    "ar",
    "as",
    "az",
    "be",
    "bg",
    "bn",
    "bs",
    "ca",
    "cs",
    "cy",
    "da",
    "de",
    "dz",
    "el",
    "en",
    "eo",
    "es",
    "et",
    "eu",
    "fa",
    "fi",
    "fo",
    "fr",
    "ga",
    "gd",
    "gl",
    "gu",
    "he",
    "hi",
    "hr",
    "hu",
    "hy",
    "id",
    "is",
    "it",
    "ja",
    "ka",
    "kk",
    "km",
    "kn",
    "ko",
    "ku",
    "ky",
    "lo",
    "lt",
    "lv",
    "mg",
    "mk",
    "ml",
    "mn",
    "mr",
    "ms",
    "mt",
    "nb",
    "ne",
    "nl",
    "nn",
    "no",
    "oc",
    "or",
    "pa",
    "pl",
    "ps",
    "pt",
    "ro",
    "ru",
    "si",
    "sk",
    "sl",
    "sq",
    "sr",
    "sv",
    "ta",
    "te",
    "th",
    "tl",
    "tr",
    "uk",
    "ur",
    "uz",
    "vi",
    "zh",
];

$languages_country = [
    "Afar",
    "Afrikaans",
    "Amharic",
    "Arabic",
    "Assamese",
    "Azerbaijani",
    "Belarusian",
    "Bulgarian",
    "Bengali",
    "Bosnian",
    "Catalan",
    "Czech",
    "Welsh",
    "Danish",
    "German",
    "Dzongkha",
    "Greek",
    "English",
    "Esperanto",
    "Spanish",
    "Estonian",
    "Basque",
    "Persian",
    "Finnish",
    "Faroese",
    "French",
    "Irish",
    "Scottish Gaelic",
    "Galician",
    "Gujarati",
    "Hebrew",
    "Hindi",
    "Croatian",
    "Hungarian",
    "Armenian",
    "Indonesian",
    "Icelandic",
    "Italian",
    "Japanese",
    "Georgian",
    "Kazakh",
    "Khmer",
    "Kannada",
    "Korean",
    "Kurdish",
    "Kyrgyz",
    "Lao",
    "Lithuanian",
    "Latvian",
    "Malagasy",
    "Macedonian",
    "Malayalam",
    "Mongolian",
    "Marathi",
    "Malay",
    "Maltese",
    "Norwegian Bokmål",
    "Nepali",
    "Dutch",
    "Norwegian Nynorsk",
    "Norwegian",
    "Occitan",
    "Oriya",
    "Punjabi",
    "Polish",
    "Pashto",
    "Portuguese",
    "Romanian",
    "Russian",
    "Sinhala",
    "Slovak",
    "Slovenian",
    "Albanian",
    "Serbian",
    "Swedish",
    "Tamil",
    "Telugu",
    "Thai",
    "Tagalog",
    "Turkish",
    "Ukrainian",
    "Urdu",
    "Uzbek",
    "Vietnamese",
    "Chinese",
];

$countries_values = [
    "AF",
    "AL",
    "DZ",
    "AD",
    "AO",
    "AR",
    "AM",
    "AU",
    "AT",
    "AZ",
    "BH",
    "BD",
    "BY",
    "BE",
    "BZ",
    "BJ",
    "BT",
    "BO",
    "BA",
    "BW",
    "BR",
    "BN",
    "BG",
    "BF",
    "BI",
    "KH",
    "CM",
    "CA",
    "CV",
    "CF",
    "TD",
    "CL",
    "CN",
    "CO",
    "KM",
    "CG",
    "CD",
    "CR",
    "HR",
    "CU",
    "CY",
    "CZ",
    "DK",
    "DJ",
    "DO",
    "EC",
    "EG",
    "SV",
    "GQ",
    "ER",
    "EE",
    "SZ",
    "ET",
    "FI",
    "FR",
    "GA",
    "GM",
    "GE",
    "DE",
    "GH",
    "GR",
    "GL",
    "GT",
    "GN",
    "GW",
    "GY",
    "HT",
    "HN",
    "HK",
    "HU",
    "IS",
    "IN",
    "ID",
    "IR",
    "IQ",
    "IE",
    "IL",
    "IT",
    "CI",
    "JM",
    "JP",
    "JO",
    "KZ",
    "KE",
    "KW",
    "KG",
    "LA",
    "LV",
    "LB",
    "LS",
    "LR",
    "LY",
    "LI",
    "LT",
    "LU",
    "MG",
    "MW",
    "MY",
    "MV",
    "ML",
    "MT",
    "MR",
    "MU",
    "MX",
    "MD",
    "MC",
    "MN",
    "ME",
    "MA",
    "MZ",
    "MM",
    "NA",
    "NP",
    "NL",
    "NZ",
    "NI",
    "NE",
    "NG",
    "MK",
    "NO",
    "OM",
    "PK",
    "PS",
    "PA",
    "PY",
    "PE",
    "PH",
    "PL",
    "PT",
    "QA",
    "RO",
    "RU",
    "RW",
    "SA",
    "SN",
    "RS",
    "SC",
    "SL",
    "SG",
    "SK",
    "SI",
    "SO",
    "ZA",
    "KR",
    "SS",
    "ES",
    "LK",
    "SD",
    "SR",
    "SE",
    "CH",
    "SY",
    "TW",
    "TJ",
    "TZ",
    "TH",
    "TG",
    "TT",
    "TN",
    "TR",
    "TM",
    "UG",
    "UA",
    "AE",
    "GB",
    "US",
    "UY",
    "UZ",
    "VE",
    "VN",
    "YE",
    "ZM",
    "ZW",
];

$countries_country = [
    "Afghanistan",
    "Albania",
    "Algeria",
    "Andorra",
    "Angola",
    "Argentina",
    "Armenia",
    "Australia",
    "Austria",
    "Azerbaijan",
    "Bahrain",
    "Bangladesh",
    "Belarus",
    "Belgium",
    "Belize",
    "Benin",
    "Bhutan",
    "Bolivia",
    "Bosnia and Herzegovina",
    "Botswana",
    "Brazil",
    "Brunei",
    "Bulgaria",
    "Burkina Faso",
    "Burundi",
    "Cambodia",
    "Cameroon",
    "Canada",
    "Cape Verde",
    "Central African Republic",
    "Chad",
    "Chile",
    "China",
    "Colombia",
    "Comoros",
    "Congo (Brazzaville)",
    "Congo (Kinshasa)",
    "Costa Rica",
    "Croatia",
    "Cuba",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Djibouti",
    "Dominican Republic",
    "Ecuador",
    "Egypt",
    "El Salvador",
    "Equatorial Guinea",
    "Eritrea",
    "Estonia",
    "Eswatini",
    "Ethiopia",
    "Finland",
    "France",
    "Gabon",
    "Gambia",
    "Georgia",
    "Germany",
    "Ghana",
    "Greece",
    "Greenland",
    "Guatemala",
    "Guinea",
    "Guinea-Bissau",
    "Guyana",
    "Haiti",
    "Honduras",
    "Hong Kong",
    "Hungary",
    "Iceland",
    "India",
    "Indonesia",
    "Iran",
    "Iraq",
    "Ireland",
    "Israel",
    "Italy",
    "Ivory Coast",
    "Jamaica",
    "Japan",
    "Jordan",
    "Kazakhstan",
    "Kenya",
    "Kuwait",
    "Kyrgyzstan",
    "Laos",
    "Latvia",
    "Lebanon",
    "Lesotho",
    "Liberia",
    "Libya",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Madagascar",
    "Malawi",
    "Malaysia",
    "Maldives",
    "Mali",
    "Malta",
    "Mauritania",
    "Mauritius",
    "Mexico",
    "Moldova",
    "Monaco",
    "Mongolia",
    "Montenegro",
    "Morocco",
    "Mozambique",
    "Myanmar",
    "Namibia",
    "Nepal",
    "Netherlands",
    "New Zealand",
    "Nicaragua",
    "Niger",
    "Nigeria",
    "North Macedonia",
    "Norway",
    "Oman",
    "Pakistan",
    "Palestine",
    "Panama",
    "Paraguay",
    "Peru",
    "Philippines",
    "Poland",
    "Portugal",
    "Qatar",
    "Romania",
    "Russia",
    "Rwanda",
    "Saudi Arabia",
    "Senegal",
    "Serbia",
    "Seychelles",
    "Sierra Leone",
    "Singapore",
    "Slovakia",
    "Slovenia",
    "Somalia",
    "South Africa",
    "South Korea",
    "South Sudan",
    "Spain",
    "Sri Lanka",
    "Sudan",
    "Suriname",
    "Sweden",
    "Switzerland",
    "Syria",
    "Taiwan",
    "Tajikistan",
    "Tanzania",
    "Thailand",
    "Togo",
    "Trinidad and Tobago",
    "Tunisia",
    "Turkey",
    "Turkmenistan",
    "Uganda",
    "Ukraine",
    "United Arab Emirates",
    "United Kingdom",
    "United States",
    "Uruguay",
    "Uzbekistan",
    "Venezuela",
    "Vietnam",
    "Yemen",
    "Zambia",
    "Zimbabwe",
];

$info_supported_locales = _T("Optionally specify additional locales to be generated.", "imaging");
$supported_locales = [
    "United States",
    "United Kingdom",
    "France",
    "Germany",
    "Spain",
    "Italy",
    "Canada",
    "Brazil",
    "Netherlands",
    "Norway",
    "Sweden",
    "Denmark",
    "Russia",
    "Japan",
    "India",
    "China",
    "Mexico",
    "South Africa",
    "Australia",
    "Belgium",
    "Portugal",
    "Switzerland",
    "Austria",
    "Israel",
    "Turkey",
    "Poland",
    "Czech Republic",
    "Romania",
    "Greece",
    "Hungary",
    "Korea (Republic of)",
    "Singapore",
];

$supported_locales_values = [
    "US",
    "GB",
    "FR",
    "DE",
    "ES",
    "IT",
    "CA",
    "BR",
    "NL",
    "NO",
    "SE",
    "DK",
    "RU",
    "JP",
    "IN",
    "CN",
    "MX",
    "ZA",
    "AU",
    "BE",
    "PT",
    "CH",
    "AT",
    "IL",
    "TR",
    "PL",
    "CZ",
    "RO",
    "GR",
    "HU",
    "KR",
    "SG",
];

$keyboard_layouts = [
    "Arabic",
    "Armenian",
    "Belarusian",
    "Belgian",
    "Bosnian",
    "Brazilian",
    "Bulgarian",
    "Canadian Multilingual",
    "Croatian",
    "Czech",
    "Danish",
    "Dutch",
    "English (US)",
    "English (UK)",
    "Estonian",
    "Finnish",
    "French",
    "German",
    "Greek",
    "Hebrew",
    "Hungarian",
    "Icelandic",
    "Italian",
    "Japanese",
    "Korean",
    "Latin American",
    "Lithuanian",
    "Macedonian",
    "Norwegian",
    "Polish",
    "Portuguese",
    "Romanian",
    "Russian",
    "Serbian",
    "Slovak",
    "Slovenian",
    "Spanish",
    "Swedish",
    "Swiss (French)",
    "Swiss (German)",
    "Turkish",
    "Ukrainian",
];

$keyboard_layouts_values = [
    "ara",
    "am",
    "by",
    "be",
    "ba",
    "br",
    "bg",
    "ca",
    "hr",
    "cz",
    "dk",
    "nl",
    "us",
    "gb",
    "ee",
    "fi",
    "fr",
    "de",
    "gr",
    "il",
    "hu",
    "is",
    "it",
    "jp",
    "kr",
    "latam",
    "lt",
    "mk",
    "no",
    "pl",
    "pt",
    "ro",
    "ru",
    "rs",
    "sk",
    "si",
    "es",
    "se",
    "ch-fr",
    "ch-de",
    "tr",
    "ua",
];

$keyboard_toggles = [
    "No toggling",
    "Alt+Caps Lock",
    "Alt+Shift",
    "Alt+Ctrl",
    "Caps Lock",
    "Both Shift keys simultaneously",
    "Control+Alt",
    "Control+Shift",
    "Left Alt",
    "Control+Shift+Alt",
    "Left Shift",
    "Left Control",
    "Right Alt (AltGr)",
    "Menu",
    "Right Shift",
    "Right Control",
    "Shift+Left Alt",
    "Shift+Caps Lock",
    "Both Alt keys simultaneously",
    "Shift+Right Alt",
    "Both Shift keys simultaneously",
    "Both Control keys simultaneously",
];

$info_enable_network = _T("Disable network configuration entirely. This is useful for cdrom installations on non-networked devices where the network questions, warning and long timeouts are a nuisance.", "imaging");

$interface_choices = [
    "auto",
    "manual",
];

$info_interface = _T("netcfg will choose an interface that has link if possible. This makes it skip displaying a list if there is more than one interface.", "imaging");
$info_link_timeout = _T("To set a different link detection timeout (default is 3 seconds).", "imaging");
$info_dhcp_timeout = _T("If you have a slow dhcp server and the installer times out waiting for it, this might be useful.", "imaging");
$info_disable_autoconfig = _T("Automatic network configuration is the default. If you prefer to configure the network manually.", "imaging");
$info_disable_dhcp = _T("If you want the preconfiguration file to work on systems both with and without a dhcp server, uncomment these lines and the static network.", "imaging");
$info_hostname = _T("Any hostname and domain names assigned from dhcp take precedence over values set here. However, setting the values still prevents the questions from being shown, even if values come from dhcp.", "imaging");
$info_dhcp_hostname = _T("The wacky dhcp hostname that some ISPs use as a password of sorts.", "imaging");
$info_load_firmware = _T("If non-free firmware is needed for the network or other hardware, you can configure the installer to always try to load it, without prompting. Or change to false to disable asking.", "imaging");
$info_network_console = _T("Use the following settings if you wish to make use of the network-console component for remote installation over SSH. This only makes sense if you intend to perform the remainder of the installation manually.", "imaging");
$info_mirror_protocol = _T("If you select ftp, the mirror/country string does not need to be set. Default value for the mirror protocol: http.", "imaging");
$mirror_protocol_values = ["http", "ftp", "rsync"];

$mirror_countries = [
    "Manual",
    "Afghanistan",
    "Albania",
    "Algeria",
    "Andorra",
    "Angola",
    "Antigua and Barbuda",
    "Argentina",
    "Armenia",
    "Australia",
    "Austria",
    "Azerbaijan",
    "Bahamas",
    "Bahrain",
    "Bangladesh",
    "Barbados",
    "Belarus",
    "Belgium",
    "Belize",
    "Benin",
    "Bhutan",
    "Bolivia",
    "Bosnia and Herzegovina",
    "Botswana",
    "Brazil",
    "Brunei",
    "Bulgaria",
    "Burkina Faso",
    "Burundi",
    "Cambodia",
    "Cameroon",
    "Canada",
    "Cape Verde",
    "Central African Republic",
    "Chad",
    "Chile",
    "China",
    "Colombia",
    "Comoros",
    "Congo, Democratic Republic of the",
    "Congo, Republic of the",
    "Costa Rica",
    "Croatia",
    "Cuba",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Djibouti",
    "Dominica",
    "Dominican Republic",
    "Ecuador",
    "Egypt",
    "El Salvador",
    "Equatorial Guinea",
    "Eritrea",
    "Estonia",
    "Eswatini",
    "Ethiopia",
    "Fiji",
    "Finland",
    "France",
    "Gabon",
    "Gambia",
    "Georgia",
    "Germany",
    "Ghana",
    "Greece",
    "Grenada",
    "Guatemala",
    "Guinea",
    "Guinea-Bissau",
    "Guyana",
    "Haiti",
    "Honduras",
    "Hungary",
    "Iceland",
    "India",
    "Indonesia",
    "Iran",
    "Iraq",
    "Ireland",
    "Israel",
    "Italy",
    "Jamaica",
    "Japan",
    "Jordan",
    "Kazakhstan",
    "Kenya",
    "Kiribati",
    "Kuwait",
    "Kyrgyzstan",
    "Laos",
    "Latvia",
    "Lebanon",
    "Lesotho",
    "Liberia",
    "Libya",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Madagascar",
    "Malawi",
    "Malaysia",
    "Maldives",
    "Mali",
    "Malta",
    "Marshall Islands",
    "Mauritania",
    "Mauritius",
    "Mexico",
    "Micronesia",
    "Moldova",
    "Monaco",
    "Mongolia",
    "Montenegro",
    "Morocco",
    "Mozambique",
    "Myanmar",
    "Namibia",
    "Nauru",
    "Nepal",
    "Netherlands",
    "New Zealand",
    "Nicaragua",
    "Niger",
    "Nigeria",
    "North Korea",
    "North Macedonia",
    "Norway",
    "Oman",
    "Pakistan",
    "Palau",
    "Palestine",
    "Panama",
    "Papua New Guinea",
    "Paraguay",
    "Peru",
    "Philippines",
    "Poland",
    "Portugal",
    "Qatar",
    "Romania",
    "Russia",
    "Rwanda",
    "Saint Kitts and Nevis",
    "Saint Lucia",
    "Saint Vincent and the Grenadines",
    "Samoa",
    "San Marino",
    "Sao Tome and Principe",
    "Saudi Arabia",
    "Senegal",
    "Serbia",
    "Seychelles",
    "Sierra Leone",
    "Singapore",
    "Slovakia",
    "Slovenia",
    "Solomon Islands",
    "Somalia",
    "South Africa",
    "South Korea",
    "South Sudan",
    "Spain",
    "Sri Lanka",
    "Sudan",
    "Suriname",
    "Sweden",
    "Switzerland",
    "Syria",
    "Taiwan",
    "Tajikistan",
    "Tanzania",
    "Thailand",
    "Timor-Leste",
    "Togo",
    "Tonga",
    "Trinidad and Tobago",
    "Tunisia",
    "Turkey",
    "Turkmenistan",
    "Tuvalu",
    "Uganda",
    "Ukraine",
    "United Arab Emirates",
    "United Kingdom",
    "United States",
    "Uruguay",
    "Uzbekistan",
    "Vanuatu",
    "Vatican City",
    "Venezuela",
    "Vietnam",
    "Yemen",
    "Zambia",
    "Zimbabwe",
];

$mirror_countries_values = [
    "manual",
    "af",
    "al",
    "dz",
    "ad",
    "ao",
    "ag",
    "ar",
    "am",
    "au",
    "at",
    "az",
    "bs",
    "bh",
    "bd",
    "bb",
    "by",
    "be",
    "bz",
    "bj",
    "bt",
    "bo",
    "ba",
    "bw",
    "br",
    "bn",
    "bg",
    "bf",
    "bi",
    "kh",
    "cm",
    "ca",
    "cv",
    "cf",
    "td",
    "cl",
    "cn",
    "co",
    "km",
    "cd",
    "cg",
    "cr",
    "hr",
    "cu",
    "cy",
    "cz",
    "dk",
    "dj",
    "dm",
    "do",
    "ec",
    "eg",
    "sv",
    "gq",
    "er",
    "ee",
    "sz",
    "et",
    "fj",
    "fi",
    "fr",
    "ga",
    "gm",
    "ge",
    "de",
    "gh",
    "gr",
    "gd",
    "gt",
    "gn",
    "gw",
    "gy",
    "ht",
    "hn",
    "hu",
    "is",
    "in",
    "id",
    "ir",
    "iq",
    "ie",
    "il",
    "it",
    "jm",
    "jp",
    "jo",
    "kz",
    "ke",
    "ki",
    "kw",
    "kg",
    "la",
    "lv",
    "lb",
    "ls",
    "lr",
    "ly",
    "li",
    "lt",
    "lu",
    "mg",
    "mw",
    "my",
    "mv",
    "ml",
    "mt",
    "mh",
    "mr",
    "mu",
    "mx",
    "fm",
    "md",
    "mc",
    "mn",
    "me",
    "ma",
    "mz",
    "mm",
    "na",
    "nr",
    "np",
    "nl",
    "nz",
    "ni",
    "ne",
    "ng",
    "kp",
    "mk",
    "no",
    "om",
    "pk",
    "pw",
    "ps",
    "pa",
    "pg",
    "py",
    "pe",
    "ph",
    "pl",
    "pt",
    "qa",
    "ro",
    "ru",
    "rw",
    "kn",
    "lc",
    "vc",
    "ws",
    "sm",
    "st",
    "sa",
    "sn",
    "rs",
    "sc",
    "sl",
    "sg",
    "sk",
    "si",
    "sb",
    "so",
    "za",
    "kr",
    "ss",
    "es",
    "lk",
    "sd",
    "sr",
    "se",
    "ch",
    "sy",
    "tw",
    "tj",
    "tz",
    "th",
    "tl",
    "tg",
    "to",
    "tt",
    "tn",
    "tr",
    "tm",
    "tv",
    "ug",
    "ua",
    "ae",
    "gb",
    "us",
    "uy",
    "uz",
    "vu",
    "va",
    "ve",
    "vn",
    "ye",
    "zm",
    "zw",
];

$timezones = [
    "Africa/Abidjan",
    "Africa/Accra",
    "Africa/Addis_Ababa",
    "Africa/Algiers",
    "Africa/Asmara",
    "Africa/Bamako",
    "Africa/Bangui",
    "Africa/Banjul",
    "Africa/Bissau",
    "Africa/Blantyre",
    "Africa/Brazzaville",
    "Africa/Bujumbura",
    "Africa/Cairo",
    "Africa/Casablanca",
    "Africa/Ceuta",
    "Africa/Conakry",
    "Africa/Dakar",
    "Africa/Dar_es_Salaam",
    "Africa/Djibouti",
    "Africa/Douala",
    "Africa/El_Aaiun",
    "Africa/Freetown",
    "Africa/Gaborone",
    "Africa/Harare",
    "Africa/Johannesburg",
    "Africa/Juba",
    "Africa/Kampala",
    "Africa/Khartoum",
    "Africa/Kigali",
    "Africa/Kinshasa",
    "Africa/Lagos",
    "Africa/Libreville",
    "Africa/Lome",
    "Africa/Luanda",
    "Africa/Lubumbashi",
    "Africa/Lusaka",
    "Africa/Malabo",
    "Africa/Maputo",
    "Africa/Maseru",
    "Africa/Mbabane",
    "Africa/Mogadishu",
    "Africa/Monrovia",
    "Africa/Nairobi",
    "Africa/Ndjamena",
    "Africa/Niamey",
    "Africa/Nouakchott",
    "Africa/Ouagadougou",
    "Africa/Porto-Novo",
    "Africa/Sao_Tome",
    "Africa/Tripoli",
    "Africa/Tunis",
    "Africa/Windhoek",
    "America/Adak",
    "America/Anchorage",
    "America/Anguilla",
    "America/Antigua",
    "America/Araguaina",
    "America/Argentina/Buenos_Aires",
    "America/Argentina/Catamarca",
    "America/Argentina/Cordoba",
    "America/Argentina/Jujuy",
    "America/Argentina/La_Rioja",
    "America/Argentina/Mendoza",
    "America/Argentina/Rio_Gallegos",
    "America/Argentina/Salta",
    "America/Argentina/San_Juan",
    "America/Argentina/San_Luis",
    "America/Argentina/Tucuman",
    "America/Argentina/Ushuaia",
    "America/Aruba",
    "America/Asuncion",
    "America/Atikokan",
    "America/Bahia",
    "America/Bahia_Banderas",
    "America/Barbados",
    "America/Belem",
    "America/Belize",
    "America/Boa_Vista",
    "America/Bogota",
    "America/Boise",
    "America/Cambridge_Bay",
    "America/Campo_Grande",
    "America/Cancun",
    "America/Caracas",
    "America/Cayenne",
    "America/Cayman",
    "America/Chicago",
    "America/Chihuahua",
    "America/Costa_Rica",
    "America/Creston",
    "America/Cuiaba",
    "America/Curacao",
    "America/Danmarkshavn",
    "America/Dawson",
    "America/Dawson_Creek",
    "America/Denver",
    "America/Detroit",
    "America/Dominica",
    "America/Edmonton",
    "America/Eirunepe",
    "America/El_Salvador",
    "America/Fort_Nelson",
    "America/Fortaleza",
    "America/Glace_Bay",
    "America/Godthab",
    "America/Goose_Bay",
    "America/Grand_Turk",
    "America/Grenada",
    "America/Guadeloupe",
    "America/Guatemala",
    "America/Guayaquil",
    "America/Guyana",
    "America/Halifax",
    "America/Havana",
    "America/Hermosillo",
    "America/Indiana/Indianapolis",
    "America/Indiana/Knox",
    "America/Indiana/Marengo",
    "America/Indiana/Petersburg",
    "America/Indiana/Tell_City",
    "America/Indiana/Vevay",
    "America/Indiana/Vincennes",
    "America/Indiana/Winamac",
    "America/Inuvik",
    "America/Iqaluit",
    "America/Jamaica",
    "America/Juneau",
    "America/Kentucky/Louisville",
    "America/Kentucky/Monticello",
    "America/La_Paz",
    "America/Lima",
    "America/Los_Angeles",
    "America/Maceio",
    "America/Managua",
    "America/Manaus",
    "America/Martinique",
    "America/Mazatlan",
    "America/Menominee",
    "America/Merida",
    "America/Mexico_City",
    "America/Miquelon",
    "America/Moncton",
    "America/Monterrey",
    "America/Montevideo",
    "America/Montreal",
    "America/Nassau",
    "America/New_York",
    "America/Nipigon",
    "America/Nome",
    "America/Noronha",
    "America/North_Dakota/Beulah",
    "America/North_Dakota/Center",
    "America/North_Dakota/New_Salem",
    "America/Ojinaga",
    "America/Panama",
    "America/Pangnirtung",
    "America/Paramaribo",
    "America/Phoenix",
    "America/Port-au-Prince",
    "America/Port_of_Spain",
    "America/Porto_Velho",
    "America/Puerto_Rico",
    "America/Punta_Arenas",
    "America/Rainy_River",
    "America/Rankin_Inlet",
    "America/Recife",
    "America/Regina",
    "America/Resolute",
    "America/Rio_Branco",
    "America/Santarem",
    "America/Santiago",
    "America/Santo_Domingo",
    "America/Sao_Paulo",
    "America/Scoresbysund",
    "America/Sitka",
    "America/St_Johns",
    "America/Swift_Current",
    "America/Tegucigalpa",
    "America/Thule",
    "America/Thunder_Bay",
    "America/Tijuana",
    "America/Toronto",
    "America/Vancouver",
    "America/Whitehorse",
    "America/Winnipeg",
    "America/Yakutat",
    "America/Yellowknife",
    "Antarctica/Casey",
    "Antarctica/Davis",
    "Antarctica/DumontDUrville",
    "Antarctica/Macquarie",
    "Antarctica/Mawson",
    "Antarctica/McMurdo",
    "Antarctica/Palmer",
    "Antarctica/Rothera",
    "Antarctica/Syowa",
    "Antarctica/Troll",
    "Antarctica/Vostok",
    "Arctic/Longyearbyen",
    "Asia/Aden",
    "Asia/Almaty",
    "Asia/Amman",
    "Asia/Anadyr",
    "Asia/Aqtau",
    "Asia/Aqtobe",
    "Asia/Ashgabat",
    "Asia/Atyrau",
    "Asia/Baghdad",
    "Asia/Bahrain",
    "Asia/Baku",
    "Asia/Bangkok",
    "Asia/Barnaul",
    "Asia/Beirut",
    "Asia/Bishkek",
    "Asia/Brunei",
    "Asia/Calcutta",
    "Asia/Chita",
    "Asia/Choibalsan",
    "Asia/Colombo",
    "Asia/Damascus",
    "Asia/Dhaka",
    "Asia/Dili",
    "Asia/Dubai",
    "Asia/Dushanbe",
    "Asia/Famagusta",
    "Asia/Gaza",
    "Asia/Hebron",
    "Asia/Ho_Chi_Minh",
    "Asia/Hong_Kong",
    "Asia/Hovd",
    "Asia/Irkutsk",
    "Asia/Jakarta",
    "Asia/Jayapura",
    "Asia/Jerusalem",
    "Asia/Kabul",
    "Asia/Kamchatka",
    "Asia/Karachi",
    "Asia/Kathmandu",
    "Asia/Khandyga",
    "Asia/Kolkata",
    "Asia/Krasnoyarsk",
    "Asia/Kuala_Lumpur",
    "Asia/Kuching",
    "Asia/Kuwait",
    "Asia/Macau",
    "Asia/Magadan",
    "Asia/Makassar",
    "Asia/Manila",
    "Asia/Muscat",
    "Asia/Nicosia",
    "Asia/Novokuznetsk",
    "Asia/Novosibirsk",
    "Asia/Omsk",
    "Asia/Oral",
    "Asia/Phnom_Penh",
    "Asia/Pontianak",
    "Asia/Pyongyang",
    "Asia/Qatar",
    "Asia/Qostanay",
    "Asia/Qyzylorda",
    "Asia/Riyadh",
    "Asia/Sakhalin",
    "Asia/Samarkand",
    "Asia/Seoul",
    "Asia/Shanghai",
    "Asia/Singapore",
    "Asia/Srednekolymsk",
    "Asia/Taipei",
    "Asia/Tashkent",
    "Asia/Tbilisi",
    "Asia/Tehran",
    "Asia/Thimphu",
    "Asia/Tokyo",
    "Asia/Tomsk",
    "Asia/Ulaanbaatar",
    "Asia/Urumqi",
    "Asia/Ust-Nera",
    "Asia/Vientiane",
    "Asia/Vladivostok",
    "Asia/Yakutsk",
    "Asia/Yangon",
    "Asia/Yekaterinburg",
    "Asia/Yerevan",
    "Atlantic/Azores",
    "Atlantic/Bermuda",
    "Atlantic/Canary",
    "Atlantic/Cape_Verde",
    "Atlantic/Faroe",
    "Atlantic/Madeira",
    "Atlantic/Reykjavik",
    "Atlantic/South_Georgia",
    "Atlantic/St_Helena",
    "Atlantic/Stanley",
    "Australia/Adelaide",
    "Australia/Brisbane",
    "Australia/Broken_Hill",
    "Australia/Currie",
    "Australia/Darwin",
    "Australia/Eucla",
    "Australia/Hobart",
    "Australia/Lindeman",
    "Australia/Lord_Howe",
    "Australia/Melbourne",
    "Australia/Perth",
    "Australia/Sydney",
    "Europe/Amsterdam",
    "Europe/Andorra",
    "Europe/Astrakhan",
    "Europe/Athens",
    "Europe/Belgrade",
    "Europe/Berlin",
    "Europe/Bratislava",
    "Europe/Brussels",
    "Europe/Bucharest",
    "Europe/Budapest",
    "Europe/Busingen",
    "Europe/Chisinau",
    "Europe/Copenhagen",
    "Europe/Dublin",
    "Europe/Gibraltar",
    "Europe/Guernsey",
    "Europe/Helsinki",
    "Europe/Isle_of_Man",
    "Europe/Istanbul",
    "Europe/Jersey",
    "Europe/Kaliningrad",
    "Europe/Kiev",
    "Europe/Kirov",
    "Europe/Lisbon",
    "Europe/Ljubljana",
    "Europe/London",
    "Europe/Luxembourg",
    "Europe/Madrid",
    "Europe/Malta",
    "Europe/Mariehamn",
    "Europe/Minsk",
    "Europe/Monaco",
    "Europe/Moscow",
    "Europe/Oslo",
    "Europe/Paris",
    "Europe/Podgorica",
    "Europe/Prague",
    "Europe/Riga",
    "Europe/Rome",
    "Europe/Samara",
    "Europe/San_Marino",
    "Europe/Sarajevo",
    "Europe/Saratov",
    "Europe/Simferopol",
    "Europe/Skopje",
    "Europe/Sofia",
    "Europe/Stockholm",
    "Europe/Tallinn",
    "Europe/Tirane",
    "Europe/Ulyanovsk",
    "Europe/Uzhgorod",
    "Europe/Vaduz",
    "Europe/Vatican",
    "Europe/Vienna",
    "Europe/Vilnius",
    "Europe/Volgograd",
    "Europe/Warsaw",
    "Europe/Zagreb",
    "Europe/Zaporozhye",
    "Europe/Zurich",
    "Indian/Antananarivo",
    "Indian/Chagos",
    "Indian/Christmas",
    "Indian/Cocos",
    "Indian/Comoro",
    "Indian/Kerguelen",
    "Indian/Mahe",
    "Indian/Maldives",
    "Indian/Mauritius",
    "Indian/Mayotte",
    "Indian/Reunion",
    "Pacific/Apia",
    "Pacific/Auckland",
    "Pacific/Bougainville",
    "Pacific/Chatham",
    "Pacific/Chuuk",
    "Pacific/Easter",
    "Pacific/Efate",
    "Pacific/Enderbury",
    "Pacific/Fakaofo",
    "Pacific/Fiji",
    "Pacific/Funafuti",
    "Pacific/Galapagos",
    "Pacific/Gambier",
    "Pacific/Guadalcanal",
    "Pacific/Guam",
    "Pacific/Honolulu",
    "Pacific/Kanton",
    "Pacific/Kiritimati",
    "Pacific/Kosrae",
    "Pacific/Kwajalein",
    "Pacific/Majuro",
    "Pacific/Marquesas",
    "Pacific/Midway",
    "Pacific/Nauru",
    "Pacific/Niue",
    "Pacific/Norfolk",
    "Pacific/Noumea",
    "Pacific/Pago_Pago",
    "Pacific/Palau",
    "Pacific/Pitcairn",
    "Pacific/Pohnpei",
    "Pacific/Port_Moresby",
    "Pacific/Rarotonga",
    "Pacific/Saipan",
    "Pacific/Tahiti",
    "Pacific/Tarawa",
    "Pacific/Tongatapu",
    "Pacific/Wake",
    "Pacific/Wallis",
    "UTC",
];

$info_services_select = _T("Select which update services to use; define the mirrors to be used. Values shown below are the normal defaults.", "imaging");
$info_add_key = _T("URL to the public key of the local repository; you must provide a key or apt will complain about the unauthenticated repository and so the sources.list line will be left commented out. or one can provide it in-line by base64 encoding the contents of the key file (with `base64 -w0`)", "imaging");
$info_run_tasksel = _T("Or choose to not get the tasksel dialog displayed at all (and don't install any packages).", "imaging");
$info_contest = _T("You can choose, if your system will report back on what software you have installed, and what software you use. The default is not to report back, but sending reports helps the project determine what software is most popular and should be included on the first CD/DVD.", "imaging");
$info_debian = _T("This is fairly safe to set, it makes grub install automatically to the UEFI partition/boot record if no other operating system is detected on the machine.", "imaging");
$info_multi = _T("This one makes grub-installer install to the UEFI partition/boot record, if it also finds some other OS, which is less safe as it might not be able to boot that other OS.", "imaging");
$info_init_partition = _T("If the system has free space you can choose to only partition that space. This is only honoured if partman-auto/method (below) is not set.", "imaging");
$info_lvm_size = _T("You can define the amount of space that will be used for the LVM volume group. It can either be a size with its unit (eg. 20 GB), a percentage of free space or the 'max' keyword.", "imaging");
$info_remove_old_lvm = _T("If one of the disks that are going to be automatically partitioned contains an old LVM configuration, the user will normally receive a warning. This can be preseeded away...", "imaging");
$info_disable_cdrom = _T("If you don't want to have the sources.list entry for a DVD/ BD installation image active in the installed system(entries for netinst or CD images will be disabled anyway, regardless of this setting).", "imaging");
$info_install_recommends = _T("Configure APT to install recommended packages by default. Use of this option can result in an incomplete system and should only be used by very experienced users.", "imaging");
$info_keep_consoles = _T("During installations from serial console, the regular virtual consoles (VT1-VT6) are normally disabled in /etc/inittab. Uncomment the next line to prevent this.", "imaging");
$info_reboot_in_progress = _T("Avoid that last message about the install being complete.", "imaging");
$info_eject_cdrom = _T("This will prevent the installer from ejecting the CD during the reboot, which is useful in some situations.", "imaging");
$info_reboot = _T("This is how to make the installer shutdown when finished, but not reboot into the installed system.", "imaging");
$info_poweroff = _T("This will power off the machine instead of just halting it.", "imaging");
$info_allow_unauth = _T("By default the installer requires that repositories be authenticated using a known gpg key. This setting can be used to disable that authentication. Warning: Insecure, not recommended.", "imaging");
?>

<script>
getExtension = (filename)=>{
    var parts = filename.split(".");
    return (parts[(parts.length-1)]);
}

jQuery( "#bvalid").click(function() {
    createCfg();
});

createCfg = ()=>{
    jQuery.post( "modules/imaging/manage/ajaxgeneratePreseedCfg.php", {
        data:  jQuery('#codeTocopy2').text(),
        title: jQuery('#Location').val()
    })
    .done(function( data1 ) {
        var file =  '  <? echo _T('File','imaging'); ?>  ';
        var avai =  ' <? echo _T('available','imaging'); ?>';
            if(data1 == 1){
                var  Msgxml1 = "Windows Answer File Generator available\non smb://"+window.location.host +"/postinst/sysprep/" +
                        jQuery('#Location').val();
                jQuery( "#spanxml" ).attr( "title", Msgxml1 );
            }
            window.location.replace("main.php?module=imaging&submod=manage&action=systemImageManager&tab=sysprepList");
    });
}

update = ()=>{
    Msgxml  = "To have the Windows Answer File Generator on \n" +
              "smb://" + window.location.host + "/postinst/sysprep/" + jQuery('#Location').val() + "\n" +
              "click on Validation" ;
    jQuery( "#spanxml" ).attr( "title", Msgxml );
    var erreur=0;
    if (jQuery('#OrginazationName').val() == ""){
            erreur = 2;
            msg = "<? echo _T('Organization Name missing','imaging'); ?>";
    }
    if( jQuery('#Location').val() == "" ||  jQuery('#Location').val() == ".xml" ){
            erreur = 1;
            msg = "<? echo _T('title missing ex : sysprep.xml','imaging'); ?>";
    }
    if(erreur != 0 ){
            jQuery("#msg_bvalid").text(msg)
            jQuery("#bvalid").prop('disabled', true);
            jQuery("#bvalid").prop('disabled', true);
            jQuery("#msg_bvalid").show();
      }
      else{
             jQuery( "#bvalid").prop('disabled', false);
             jQuery("#msg_bvalid").hide();

      }

    da=new Date()
    var dateval = da.getFullYear()+ '-'+(da.getMonth()+1) + '-' + da.getDate()

    var variables = {
        'Location': jQuery('#Location').val(),
        'dateval': dateval,
        'Comments': jQuery('#Comments').val(),
        'CheckLocale': (jQuery('#check-locale').is(":checked") ? '' : '#'),
        'SelectLocale': jQuery('#select-locale').find('option:selected').val(),
        'CheckLanguage': (jQuery('#check-language').is(":checked") ? '' : '#'),
        'SelectLanguage': jQuery('#select-language').find('option:selected').val(),
        'CheckCountry': (jQuery('#check-country').is(":checked") ? '' : '#'),
        'SelectCountry': jQuery('#select-country').find('option:selected').val(),
        'CheckSupportedCountry' : jQuery('#check-supported-country').is(":checked") ? "" : "#",
        'SelectSupportedCountry': jQuery('#select-supported-country').find('option:selected').val(),
        'CheckSupportedLocales' : jQuery('#check-supported-locales').is(":checked") ? "" : "#",
        'SelectSupportedLocales': jQuery('#select-supported-locales').find('option:selected').val(),
        'CheckKeyboardLayouts' : jQuery('#check-keyboard-layouts').is(":checked") ? "" : "#",
        'SelectKeyboardLayouts': jQuery('#select-keyboard-layouts').find('option:selected').val(),
        'CheckKeyboardToggle' : jQuery('#check-keyboard-toggle').is(":checked") ? "" : "#",
        'SelectKeyboardToggle': jQuery('#select-keyboard-toggle').find('option:selected').val(),
        'CheckEnableNetwork':jQuery("#check-enable-network").is(":checked") ? "" : "#",
        'CheckEnableNetworkValue':jQuery("#check-enable-network-value").is(":checked") ? "true" : "false",
        'CheckInterface' : jQuery("#check-interface").is(":checked") ? "" : "#",
        'SelectInterface' : jQuery("#select-interface").find('option:selected').val(),
        'InputInterface' : jQuery("#select-interface").find('option:selected').val() == 'auto' ? 'auto' : jQuery("#input-interface").val(),
        'CheckLinkTimeout': jQuery("#check-link-timeout").is(":checked") ? "" : "#",
        'NumberLinkTimeout':jQuery("#number-link-timeout").val(),
        'CheckDhcpTimeout': jQuery("#check-dhcp-timeout").is(":checked") ? "" : "#",
        'NumberDhcpTimeout':jQuery("#number-dhcp-timeout").val(),
        'CheckDhcpV6Timeout': jQuery("#check-dhcpv6-timeout").is(":checked") ? "" : "#",
        'NumberDhcpV6Timeout':jQuery("#number-dhcpv6-timeout").val(),
        'CheckDisableAutoconfig': jQuery("#check-disable-autoconfig").is(":checked") ? "" : "#",
        'CheckDisableAutoconfigValue': jQuery("#check-disable-autoconfig-value").is(":checked") ? "true" : "false",
        'CheckDisableDhcp' : jQuery("#check-disable-dhcp").is(":checked") ? '' : '#',
        'CheckDisableDhcpValue' : jQuery('#check-disable-dhcp-value').is(":checked") ? "true" : "false",
        'CheckDisableDhcpCombine' : jQuery('#check-disable-dhcp-value').is(":checked") ? "" : "#", // Alias for dhcpValue, to put a comment tag or not on the beginning of the static conf
        'InputGetIpaddress' : jQuery("#input-get-ipaddress").val(),
        'InputGetNetmask' :  jQuery("#input-get-netmask").val(),
        'InputGetGateway' : jQuery("#input-get-gateway").val(),
        'InputGetNameservers' : jQuery("#input-get-nameservers").val(),
        'CheckHostname': jQuery("#check-hostname").is(":checked") ? '' : '#',
        'InputHostname' : jQuery("#input-hostname").val(),
        'CheckDomaine': jQuery("#check-domaine").is(":checked") ? '' : '#',
        'InputDomaine' : jQuery("#input-domaine").val(),
        'CheckForceHostname': jQuery("#check-force-hostname").is(":checked") ? '' : '#',
        'InputForceHostname' : jQuery("#input-force-hostname").val(),
        'CheckDhcpHostname': jQuery("#check-dhcp-hostname").is(":checked") ? '' : '#',
        'InputDhcpHostname' : jQuery("#input-dhcp-hostname").val(),
        'CheckLoadFirmware': jQuery("#check-load-firmware").is(":checked") ? '' : '#',
        'CheckLoadFirmwareValue': jQuery("#check-load-firmware-value").is(":checked") ? 'true' : 'false',
        'CheckNetworkConsole' : jQuery("#check-network-console").is(":checked") ? '' : '#',
        'CheckNetworkConsoleType' : jQuery("#check-network-console-value").is(":checked") ? 'string' : 'boolean',
        'CheckNetworkConsoleValue' : jQuery("#check-network-console-value").is(":checked") ? 'network-console' : 'false',
        'CheckAuthorizedKeysUrl' : jQuery("#check-authorized-keys-url").is(":checked") ? '' : '#',
        'InputAuthorizedKeysUrl' : jQuery("#input-authorized-keys-url").val(),
        'CheckMirrorProtocol' : jQuery("#check-mirror-protocol").is(":checked") ? '' : '#',
        'SelectMirrorProtocol': jQuery("#select-mirror-protocol").find('option:selected').val(),
        'InputMirrorHostname': jQuery("#input-mirror-hostname").val(),
        'InputMirrorDirectory': jQuery("#input-mirror-directory").val(),
        'InputMirrorProxy': jQuery("#input-mirror-proxy").val(),
        'CheckMirrorCountry': jQuery("#check-mirror-country").is(":checked") ? '' : '#',
        'SelectMirrorCountry': jQuery("#select-mirror-country").find("option:selected").val(),
        'CheckMirrorSuite': jQuery("#check-mirror-suite").is(":checked") ? '' : '#',
        'InputMirrorSuite': jQuery("#input-mirror-suite").val(),
        'CheckMirrorSuiteComponents': jQuery("#check-mirror-suite-components").is(":checked") ? '' : '#',
        'InputMirrorSuiteComponents': jQuery("#input-mirror-suite-components").val(),
        'CheckSkipRootLogin' : jQuery("#check-skip-root-login").is(":checked") ? '' : '#',
        'CheckSkipRootLoginValue' : jQuery("#check-skip-root-login-value").is(":checked") ? 'true' : 'false',
        'CheckRootPasswd' : jQuery("#check-root-passwd").is(":checked") ? '' : '#',
        'InputRootPasswd' : jQuery("#input-root-passwd").val(),
        'CheckMakeUser' : jQuery("#check-makeuser").is(":checked") ? '' : '#',
        'CheckMakeUserValue' : jQuery("#check-makeuser-value").is(":checked") ? 'true' : 'false',
        'CheckUserFullname' : jQuery("#check-user-fullname").is(":checked") ? '' : '#',
        'InputUserFullname' : jQuery("#input-user-fullname").val(),
        'CheckUsername' : jQuery("#check-username").is(":checked") ? '' : '#',
        'InputUsername' : jQuery("#input-username").val(),
        'CheckUserPasswd' : jQuery("#check-user-passwd").is(":checked") ? '' : '#',
        'InputUserPasswd' : jQuery("#input-user-passwd").val(),
        'CheckUserUid' : jQuery("#check-user-uid").is(":checked") ? '' : '#',
        'NumberUserUid' : jQuery("#number-user-uid").val(),
        'CheckUserGroup' : jQuery("#check-user-group").is(":checked") ? '' : '#',
        'InputUserGroup' : jQuery("#input-user-group").val(),
        'CheckUtc': jQuery("#check-utc").is(":checked") ? '' : '#',
        'CheckUtcValue': jQuery("#check-utc-value").is(":checked") ? 'true' : 'false',
        'CheckTimezone': jQuery("#check-timezone").is(":checked") ? '' : '#',
        'SelectTimezone': jQuery("#select-timezone").val(),
        'CheckInitPartition' : jQuery("#check-init-partition").is(":checked") ? '' : '#',
        'SelectInitPartition' : jQuery("#select-init-partition").val(),
        'CheckLvmSize' : jQuery("#check-lvm-size").is(":checked") ? '' : '#',
        'InputLvmSize' : jQuery("#input-lvm-size").val(),
        'CheckRemoveOldLvm' : jQuery("#check-remove-old-lvm").is(":checked") ? '' : '#',
        'CheckRemoveOldLvmValue' : jQuery("#check-remove-old-lvm-value").is(":checked") ? 'true' : 'false',
        'CheckLvmConfirm' : jQuery("#check-lvm-confirm").is(":checked") ? '' : '#',
        'CheckLvmConfirmValue' : jQuery("#check-lvm-confirm-value").is(":checked") ? 'true' : 'false',
        'CheckLvmNoOverwrite' : jQuery("#check-lvm-nooverwrite").is(":checked") ? '' : '#',
        'CheckLvmNoOverwriteValue' : jQuery("#check-lvm-nooverwrite-value").is(":checked") ? 'true' : 'false',
        'CheckInstallRecommends' : jQuery("#check-install-recommends").is(":checked") ? '' : '#',
        'CheckInstallRecommendsValue' : jQuery("#check-install-recommends-value").is(":checked") ? 'true': 'false',
        'CheckKernelImage' : jQuery("#check-kernel-image").is(":checked") ? '' : '#',
        'InputKernelImage' : jQuery("#input-kernel-image").val(),
        'CheckSetFirst' : jQuery("#check-set-first").is(":checked") ? '' : '#',
        'CheckSetFirstValue' : jQuery("#check-set-first-value").is(":checked") ? 'true' : 'false',
        'CheckNonFreeFirmware' : jQuery("#check-non-free-firmware").is(":checked") ? '' : '#',
        'CheckNonFreeFirmwareValue' : jQuery("#check-non-free-firmware-value").is(":checked") ? 'true' : 'false',
        'CheckNonFree' : jQuery("#check-non-free").is(":checked") ? '' : '#',
        'CheckNonFreeValue' : jQuery("#check-non-free-value").is(":checked") ? 'true' : 'false',
        'CheckContrib' : jQuery("#check-contrib").is(":checked") ? '' : '#',
        'CheckContribValue' : jQuery("#check-contrib-value").is(":checked") ? 'true' : 'false',
        'CheckDisableCdrom' : jQuery("#check-disable-cdrom").is(":checked") ? '' : '#',
        'CheckDisableCdromValue' : jQuery("#check-disable-cdrom-value").is(":checked") ? 'true' : 'false',
        'CheckUseMirror' : jQuery("#check-use-mirror").is(":checked") ? '' : '#',
        'CheckUseMirrorValue' : jQuery("#check-use-mirror-value").is(":checked") ? 'true' : 'false',
        'CheckKeepConsoles' : jQuery("#check-keep-consoles").is(":checked") ? '' : '#',
        'CheckKeepConsolesValue' : jQuery("#check-keep-consoles-value").is(":checked") ? 'true' : 'false',
        'CheckRebootInProgress' : jQuery("#check-reboot-in-progress").is(":checked") ? '' : '#',
        'CheckRebootInProgressValue' : jQuery("#check-reboot-in-progress-value").is(":checked") ? 'true' : 'false',
        'CheckEjectCdrom' : jQuery("#check-eject-cdrom").is(":checked") ? '' : '#',
        'CheckEjectCdromValue' : jQuery("#check-eject-cdrom-value").is(":checked") ? 'true' : 'false',
        'CheckReboot' : jQuery("#check-reboot").is(":checked") ? '' : '#',
        'CheckRebootValue' : jQuery("#check-reboot-value").is(":checked") ? 'true' : 'false',
        'CheckPoweroff' : jQuery("#check-poweroff").is(":checked") ? '' : '#',
        'CheckPoweroffValue' : jQuery("#check-poweroff-value").is(":checked") ? 'true' : 'false',
        'CheckServicesSelect' : jQuery("#check-services-select").is(":checked") ? '' : '#',
        'InputServicesSelect' : jQuery("#input-services-select").val(),
        'CheckSecurityHost' : jQuery("#check-security-host").is(":checked") ? '' : '#',
        'InputSecurityHost': jQuery("#input-security-host").val(),
        'CheckAddRepo': jQuery("#check-add-repo").is(":checked") ? '' : '#',
        'InputAddRepo': jQuery("#input-add-repo").val(),
        'CheckAddComment': jQuery("#check-add-comment").is(":checked") ? '' : '#',
        'InputAddComment': jQuery("#input-add-comment").val(),
        'CheckAddSource': jQuery("#check-add-source").is(":checked") ? '' : '#',
        'CheckAddSourceValue': jQuery("#check-add-source-value").is(":checked") ? "true" : "false",
        'CheckAddKey': jQuery("#check-add-key").is(":checked") ? "" : "#",
        'InputAddKey': jQuery("#input-add-key").val(),
        'CheckAllowUnauth' : jQuery("#check-allow-unauth").is(":checked") ? "" : "#",
        'CheckAllowUnauthValue' : jQuery("#check-allow-unauth-value").is(":checked") ? "true" : "false",
        "CheckMultiArch" : jQuery("#check-multi-arch").is(":checked") ? "" : "#",
        "InputMultiArch" : jQuery("#input-multi-arch").val(),
        "CheckTasksel" : jQuery("#check-tasksel").is(":checked") ? '' : '#',
        "InputTasksel" : jQuery("#input-tasksel").val(),
        "CheckRunTasksel" : jQuery("#check-run-tasksel").is(":checked") ? '' : '#',
        "InputRunTasksel" : jQuery("#input-run-tasksel").val(),
        "CheckInclude" : jQuery("#check-include").is(":checked") ? '' : '#',
        "InputInclude" : jQuery("#input-include").val(),
        "CheckUpgrade" : jQuery("#check-upgrade").is(":checked") ? '' : '#',
        "SelectUpgrade": jQuery("#select-upgrade").val(),
        "CheckContest" : jQuery("#check-contest").is(":checked") ? '' : '#',
        "CheckContestValue" : jQuery("#check-contest-value").is(":checked") ? 'true' : 'false',
        "CheckDebian" : jQuery("#check-debian").is(":checked") ? '' : '#',
        "CheckDebianValue" : jQuery("#check-debian").is(":checked") ? 'true' : 'false',
        "CheckMulti" : jQuery("#check-multi").is(":checked") ? '' : '#',
        "CheckMultiValue" : jQuery("#check-multi").is(":checked") ? 'true' : 'false',

    };// End of bind

    listParameters={}

    var newConfig = template.replace(/<\?(\w+)\?>/g,
    function(match, name) {
        if(!((name == "dateval") || (name == "Location") || (name == "Comments")))
            listParameters[name]=variables[name];

        return variables[name];
    });
    var myJsonString = JSON.stringify(listParameters);

    var newConfig = template.replace(/<\?(\w+)\?>/g,
    (match, name) => {
        if(!((name == "dateval") || (name == "Location") || (name == "Comments")))
            listParameters[name]=variables[name];

        return variables[name];
    });
    newConfig = newConfig.replace("@@listParameters@@",myJsonString);

    jQuery('input[name=codeToCopy]').val(newConfig);
        jQuery.post( "modules/imaging/manage/ajaxFormatLinux.php", { data: newConfig })
            .done(( data1 ) => {
                jQuery('#codeTocopy2').html(data1);
        });
}

fn_Installation_Notes=function(){
    var list_hidden_ids=['Comments'];
    jQuery.each(list_hidden_ids, function( index,value) {
        jQuery('#'+value).parents("tr").toggle();
    });
    if (jQuery('#'+list_hidden_ids[0]).is(":visible")){
        jQuery('#Installation_Notes').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
    }
    else{
        jQuery('#Installation_Notes').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
    }
};


fn_Locale=function(){
    var list_hidden_ids=[
        // "select-locale",
        "select-language",
        "select-country",
        "select-supported-locales",
        // "select-keyboard-layouts",
        "select-keyboard-toggle",
    ];
    jQuery.each(list_hidden_ids, function( index,value) {
        jQuery('#'+value).parents("tr").toggle();
    });
    if (jQuery('#'+list_hidden_ids[0]).is(":visible")){
        jQuery('#Locale').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
    }
    else{
        jQuery('#Locale').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
    }
};

fn_Network=function(){
    var list_hidden_ids=[
    "check-enable-network-value",
    "select-interface",
    "number-link-timeout",
    "number-dhcp-timeout",
    "number-dhcpv6-timeout",
    // "check-disable-autoconfig-value",
    // "check-disable-dhcp-value",
    "input-hostname",
    "input-domaine",
    "input-force-hostname",
    "input-dhcp-hostname",
    "check-load-firmware-value",

    ];
    jQuery.each(list_hidden_ids, function( index,value) {
        jQuery('#'+value).parents("tr").toggle();
    });
    if (jQuery('#'+list_hidden_ids[0]).is(":visible")){
        jQuery('#Network').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
    }
    else{
        jQuery('#Network').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
    }
};


fn_NetworkConsole=function(){
    var list_hidden_ids=[
        "check-network-console-value",
        "input-authorized-keys-url",
    ];
    jQuery.each(list_hidden_ids, function( index,value) {
        jQuery('#'+value).parents("tr").toggle();
    });
    if (jQuery('#'+list_hidden_ids[0]).is(":visible")){
        jQuery('#NetworkConsole').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
    }
    else{
        jQuery('#NetworkConsole').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
    }
};


fn_Mirror=function(){
    var list_hidden_ids=[
        // "select-mirror-protocol",
        "select-mirror-country",
        // "input-mirror-suite",
        "input-mirror-suite-components",

    ];
    jQuery.each(list_hidden_ids, function( index,value) {
        jQuery('#'+value).parents("tr").toggle();
    });
    if (jQuery('#'+list_hidden_ids[0]).is(":visible")){
        jQuery('#Mirror').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
    }
    else{
        jQuery('#Mirror').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
    }
};

fn_Accounts=function(){
    var list_hidden_ids=[
        "check-skip-root-login-value",
        "check-skip-makeuser-value",
        "check-user-fullname",
        "check-user-uid",
        "check-user-group",
    ];
    jQuery.each(list_hidden_ids, function( index,value) {
        jQuery('#'+value).parents("tr").toggle();
    });
    if (jQuery('#'+list_hidden_ids[0]).is(":visible")){
        jQuery('#Accounts').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
    }
    else{
        jQuery('#Accounts').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
    }
};

fn_Timezone=function(){
    var list_hidden_ids=[
        "check-utc"
    ];
    jQuery.each(list_hidden_ids, function( index,value) {
        jQuery('#'+value).parents("tr").toggle();
    });
    if (jQuery('#'+list_hidden_ids[0]).is(":visible")){
        jQuery('#Timezone').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
    }
    else{
        jQuery('#Timezone').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
    }
};


fn_Partitionning=function(){
    var list_hidden_ids=[
        "check-lvm-nooverwrite",
    ];
    jQuery.each(list_hidden_ids, function( index,value) {
        jQuery('#'+value).parents("tr").toggle();
    });
    if (jQuery('#'+list_hidden_ids[0]).is(":visible")){
        jQuery('#Partitionning').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
    }
    else{
        jQuery('#Partitionning').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
    }
};

fn_Validate=function(){
    var list_hidden_ids=[
        "codeTocopy2"
    ];
    jQuery.each(list_hidden_ids, function( index,value) {
        jQuery('#'+value).toggle();
    });

    if (jQuery('#'+list_hidden_ids[0]).is(":visible")){
        jQuery('#Validate').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
    }
    else{
        jQuery('#Validate').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
    }
};

fn_BaseSystemInstallation = ()=>{
    var list_hidden_ids=[
        "check-kernel-image",
    ];
    jQuery.each(list_hidden_ids, function( index,value) {
        jQuery('#'+value).parents("tr").toggle();
    });
    if (jQuery('#'+list_hidden_ids[0]).is(":visible")){
        jQuery('#BaseSystemInstallation').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
    }
    else{
        jQuery('#BaseSystemInstallation').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
    }
};

fn_Aptsetup = ()=>{
       var list_hidden_ids=[
        "check-set-first",
        "check-non-free-firmware",
        "check-non-free",
        "check-contrib",
        "check-disable-cdrom",
        "check-use-mirror",
        "check-services-select",
        "check-security-host",
        "check-add-repo",
        "check-add-comment",
        "check-add-source",
        "check-add-key",
        "check-allow-unauth",
        "check-multi-arch",
    ];
    jQuery.each(list_hidden_ids, function( index,value) {
        jQuery('#'+value).parents("tr").toggle();
    });
    if (jQuery('#'+list_hidden_ids[0]).is(":visible")){
        jQuery('#Aptsetup').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
    }
    else{
        jQuery('#Aptsetup').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
    }
};

fn_PackageSelection = ()=>{
       var list_hidden_ids=[
        "check-run-tasksel",
        "check-upgrade",
        "check-contest",
    ];
    jQuery.each(list_hidden_ids, function( index,value) {
        jQuery('#'+value).parents("tr").toggle();
    });
    if (jQuery('#'+list_hidden_ids[0]).is(":visible")){
        jQuery('#PackageSelection').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
    }
    else{
        jQuery('#PackageSelection').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
    }
};

fn_BootLoader = ()=>{
       var list_hidden_ids=[
        "check-debian",
        "check-multi"
    ];
    jQuery.each(list_hidden_ids, function( index,value) {
        jQuery('#'+value).parents("tr").toggle();
    });
    if (jQuery('#'+list_hidden_ids[0]).is(":visible")){
        jQuery('#BootLoader').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
    }
    else{
        jQuery('#BootLoader').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
    }
};

fn_Finishing = ()=>{
       var list_hidden_ids=[
        "check-keep-consoles",
        "check-reboot-in-progress",
        "check-eject-cdrom",
    ];
    jQuery.each(list_hidden_ids, function( index,value) {
        jQuery('#'+value).parents("tr").toggle();
    });
    if (jQuery('#'+list_hidden_ids[0]).is(":visible")){
        jQuery('#Finishing').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
    }
    else{
        jQuery('#Finishing').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
    }
};

enable_item = (selector) =>{
    jQuery(selector).prop("disabled", false)
}

disable_item = (selector) =>{
    jQuery(selector).prop("disabled", true)
}

toggle_item = (selector) => {
    if(jQuery(selector).prop("disabled") == true){
        jQuery(selector).prop("disabled", false)
    }
    else{
        jQuery(selector).prop("disabled", true)
    }
}

init_item = (checkSelector, valueSelector) =>{
    if(jQuery(checkSelector).is(":checked")){
        enable_item(valueSelector)
    }
    else{
        disable_item(valueSelector)
    }
}
jQuery(function () {
    // On form loading, disable elements if the checkbox is not selected
    init_item("#check-locale", "#select-locale")
    init_item("#check-language", "#select-language")
    init_item("#check-country", "#select-country")
    init_item("#check-supported-locales", "#select-supported-locales")
    init_item("#check-keyboard-layouts", "#select-keyboard-layouts")
    init_item("#check-keyboard-toggle", "#select-keyboard-toggle")
    init_item("#check-enable-network", "#check-enable-network-value")
    init_item("#check-link-timeout", "#number-link-timeout")
    init_item("#check-dhcp-timeout", "#number-dhcp-timeout")
    init_item("#check-dhcpv6-timeout", "#number-dhcpv6-timeout")
    init_item("#check-disable-autoconfig", "#check-disable-autoconfig-value")

    // Specific initialization
    if(jQuery("#check-disable-dhcp").is(":checked")){
        enable_item("#select-interface")
        if(jQuery("#select-interface").val() == "auto"){
            jQuery("#input-interface").prop("disabled", true)
        }
        else{
            jQuery("#input-interface").prop("disabled", false)
        }
    }
    else{
        disable_item("#select-interface")
        disable_item("#input-interface")
    }


    // Disable dhcp
    if(jQuery("#check-disable-dhcp").is(":checked")){
        enable_item("#check-disable-dhcp-value");
        if(jQuery("#check-disable-dhcp-value").is(":checked")){
            enable_item("#input-get-ipaddress")
            enable_item("#input-get-netmask")
            enable_item("#input-get-gateway")
            enable_item("#input-get-nameservers")
        }
    }
    else{
        disable_item("#check-disable-dhcp-value")
        disable_item("#input-get-ipaddress")
        disable_item("#input-get-netmask")
        disable_item("#input-get-gateway")
        disable_item("#input-get-nameservers")
    }

    init_item("#check-hostname", "#input-hostname");
    init_item("#check-domaine", "#input-domaine");
    init_item("#check-force-hostname", "#input-force-hostname");
    init_item("#check-dhcp-hostname", "#input-dhcp-hostname");
    init_item("#check-load-firmware", "#check-load-firmware-value");
    init_item("#check-network-console", "#check-network-console-value");
    init_item("#check-authorized-keys-url", "#input-authorized-keys-url");
    init_item("#check-root-passwd", "#input-root-passwd");
    init_item("#check-makeuser", "#check-makeuser-value");

    if(jQuery("#check-mirror-protocol").is(":checked")){
        enable_item("#select-mirror-protocol")
        enable_item("#input-mirror-hostname")
        enable_item("#input-mirror-directory")
        enable_item("#input-mirror-proxy")
    }
    else{
        disable_item("#select-mirror-protocol")
        disable_item("#input-mirror-hostname")
        disable_item("#input-mirror-directory")
        disable_item("#input-mirror-proxy")
    }

    init_item("#check-mirror-country", "#select-mirror-country")
    init_item("#check-mirror-suite", "#input-mirror-suite")
    init_item("#check-mirror-suite-components", "#input-mirror-suite-components")
    init_item("#check-skip-root-login", "#check-skip-root-login-value")
    init_item("#check-user-fullname", "#input-user-fullname")
    init_item("#check-username", "#input-username")
    init_item("#check-user-passwd", "#input-user-passwd")
    init_item("#check-user-uid", "#number-user-uid")
    init_item("#check-user-group", "#input-user-group")
    init_item("#check-utc", "#check-utc-value")
    init_item("#check-timezone", "#select-timezone")
    init_item("#check-init-partition", "#select-init-partition")
    init_item("#check-lvm-size", "#input-lvm-size")
    init_item("#check-remove-old-lvm", "#check-remove-old-lvm-value")
    init_item("#check-lvm-confirm", "#check-lvm-confirm-value")
    init_item("#check-lvm-nooverwrite", "#check-lvm-nooverwrite-value")
    init_item("#check-install-recommends", "#check-install-recommends-value")
    init_item("#check-kernel-image", "#input-kernel-image")
    init_item('#check-set-first', '#check-set-first-value')
    init_item('#check-non-free-firmware', '#check-non-free-firmware-value')
    init_item('#check-non-free', '#check-non-free-value')
    init_item('#check-contrib', '#check-contrib-value')
    init_item('#check-disable-cdrom', '#check-disable-cdrom-value')
    init_item('#check-use-mirror', '#check-use-mirror-value')
    init_item("#check-keep-consoles", "#check-keep-consoles-value")
    init_item("#check-reboot-in-progress", "#check-reboot-in-progress-value")
    init_item("#check-eject-cdrom", "#check-eject-cdrom-value")
    init_item("#check-reboot", "#check-reboot-value")
    init_item("#check-poweroff", "#check-poweroff-value")
    init_item("#check-services-select", "#input-services-select")
    init_item("#check-security-host", "#input-security-host")
    init_item("#check-add-repo", "#input-add-repo")
    init_item("#check-add-comment", "#input-add-comment")
    init_item("#check-add-source", "#check-add-source-value")
    init_item("#check-add-key", "#input-add-key")
    init_item("#check-allow-unauth", "#check-allow-unauth-value")
    init_item("#check-multi-arch", "#input-multi-arch")
    init_item("#check-tasksel", "#input-tasksel")
    init_item("#check-run-tasksel", "#input-run-tasksel")
    init_item("#check-include", "#input-include")
    init_item("#check-upgrade", "#select-upgrade")
    init_item("#check-contest", "#check-contest-value")
    init_item("#check-debian", "#check-debian-value")
    init_item("#check-multi", "#check-multi-value")

    jQuery("#codeTocopy2").toggle();
    // ----
    // CHANGE section
    // ----


    jQuery('#Comments').bind('input propertychange', function() { update();});
    jQuery( '#Location' ).on('change', function () {
        if(getExtension( jQuery('#Location').val() ) != "cfg"){
            var namefile=jQuery('#Location').val() + ".cfg"
            jQuery('#Location').val( namefile )
        }
        jQuery("#Location").val(jQuery("#Location").val().replace(/ /g,"_"));
        update();
    });

    jQuery('#check-locale' ).on( 'change', ()=>{
        toggle_item("#select-locale");
        update();
    });
    jQuery('#select-locale').on('change', ()=>{update();});
    jQuery('#check-language').on('change', ()=>{
        toggle_item("#select-language");
        update();
    });
    jQuery('#select-language').on('change', ()=>{update();});

    jQuery('#check-country').on('change', ()=>{
        toggle_item("#select-country");
        update();
    });
    jQuery('#select-country').on('change', ()=>{update();});


    jQuery('#check-supported-locales').on('change', ()=>{
        toggle_item("#select-supported-locales");
        update();
    });
    jQuery("#select-supported-locales").on("change", ()=>{update()});

    jQuery('#check-keyboard-layouts').on('change', ()=>{
        toggle_item("#select-keyboard-layouts");
        update();
    });

    jQuery("#select-keyboard-layouts").on("change", ()=>{update()});

    jQuery('#check-keyboard-toggle').on('change', ()=>{
        toggle_item("#select-keyboard-toggle");
        update();
    });

    jQuery("#select-keyboard-toggle").on("change", ()=>{update()});

    jQuery("#check-enable-network").on("change", ()=>{
        toggle_item("#check-enable-network-value");
        update()
    });
    jQuery('#check-enable-network-value').on("change", ()=>{update()});
    jQuery("#select-interface").on("change", ()=>{
        if(jQuery('#select-interface').val() == "manual"){
            enable_item("#input-interface")
        }
        else{
            disable_item("#input-interface")
        }
        update()
    })
    jQuery('#check-interface').on("change", ()=>{
        toggle_item("#select-interface");
        if(jQuery('#select-interface').prop('disabled') == true){
            disable_item("#input-interface")
        }
        else{
            if(jQuery('#select-interface').val() == "manual"){
                enable_item("#input-interface")
            }
            else{
                disable_item("#input-interface")
            }
        }
        update()
    });

    jQuery('#select-interface').on("change", ()=>{update()});

    jQuery("#input-interface").on("change", ()=>{update()});

    jQuery('#check-link-timeout').on('change', ()=>{
        toggle_item("#number-link-timeout");
        update();
    });
    jQuery("#number-link-timeout").on("change", ()=>{update()});

    jQuery('#check-dhcp-timeout').on('change', ()=>{
        toggle_item("#number-dhcp-timeout");
        update();
    });
    jQuery("#number-dhcp-timeout").on("change", ()=>{update()});

    jQuery('#check-dhcpv6-timeout').on('change', ()=>{
        toggle_item("#number-dhcpv6-timeout");
        update();
    });
    jQuery("#number-dhcpv6-timeout").on("change", ()=>{update()});

    jQuery("#check-disable-autoconfig").on('change', ()=>{
        toggle_item("#check-disable-autoconfig-value");
        update()}
    );
    jQuery("#check-disable-autoconfig-value").on('change', ()=>{update()})

    jQuery("#check-disable-dhcp").on("change", ()=>{
        toggle_item("#check-disable-dhcp-value");

        if(jQuery("#check-disable-dhcp").is(":checked")){
            if(jQuery("#check-disable-dhcp-value").is(":checked")){
                enable_item("#input-get-ipaddress");
                enable_item("#input-get-netmask");
                enable_item("#input-get-gateway");
                enable_item("#input-get-nameservers");
            }
            else{
                disable_item("#input-get-ipaddress");
                disable_item("#input-get-netmask");
                disable_item("#input-get-gateway");
                disable_item("#input-get-nameservers");
            }
        }
        else{
            disable_item("#check-disable-dhcp-value");
            disable_item("#input-get-ipaddress");
            disable_item("#input-get-netmask");
            disable_item("#input-get-gateway");
            disable_item("#input-get-nameservers");
        }
        update();
    })

    jQuery("#check-disable-dhcp-value").on("change", ()=>{
            if(jQuery("#check-disable-dhcp-value").is(":checked")){
                enable_item("#input-get-ipaddress");
                enable_item("#input-get-netmask");
                enable_item("#input-get-gateway");
                enable_item("#input-get-nameservers");
            }
            else{
                disable_item("#input-get-ipaddress");
                disable_item("#input-get-netmask");
                disable_item("#input-get-gateway");
                disable_item("#input-get-nameservers");
            }
        update()
    })
    jQuery("#input-get-ipaddress").on("change", ()=>{update()
    })
    jQuery("#input-get-netmask").on("change", ()=>{update()})
    jQuery("#input-get-gateway").on("change", ()=>{update()})
    jQuery("#input-get-nameservers").on("change", ()=>{update()})


    jQuery("#check-hostname").on("change", ()=>{
        toggle_item("#input-hostname");
        update();
    })
    jQuery('#input-hostname').on("change", ()=>{update()});


    jQuery("#check-domaine").on("change", ()=>{
        toggle_item("#input-domaine");
        update();
    })
    jQuery('#input-domaine').on("change", ()=>{update()});


    jQuery("#check-force-hostname").on("change", ()=>{
        toggle_item("#input-force-hostname");
        update();
    })
    jQuery('#input-force-hostname').on("change", ()=>{update()});


    jQuery('#check-dhcp-hostname').on("change", ()=>{
        toggle_item("#input-dhcp-hostname");
        update();
    })
    jQuery('#input-dhcp-hostname').on("change", ()=>{update()});


    jQuery('#check-load-firmware').on("change", ()=>{
        toggle_item("#check-load-firmware-value");
        update();
    })
    jQuery('#check-load-firmware-value').on("change", ()=>{update();})


    jQuery('#check-network-console').on("change", ()=>{
        toggle_item("#check-network-console-value");
        update();
    })
    jQuery('#check-network-console-value').on("change", ()=>{update();})


    jQuery("#check-authorized-keys-url").on("change", ()=>{
        toggle_item("#input-authorized-keys-url");
        update();
    })
    jQuery("#input-authorized-keys-url").on("change", ()=>{update()})

    jQuery("#check-mirror-protocol").on("change", ()=>{
        if(jQuery("#check-mirror-protocol").is(":checked")){
            enable_item("#select-mirror-protocol")
            enable_item("#input-mirror-hostname")
            enable_item("#input-mirror-directory")
            enable_item("#input-mirror-proxy")
        }
        else{
            disable_item("#select-mirror-protocol")
            disable_item("#input-mirror-hostname")
            disable_item("#input-mirror-directory")
            disable_item("#input-mirror-proxy")
        }
    })
    jQuery("#check-mirror-protocol").on("change", ()=>{update()})
    jQuery("#select-mirror-protocol").on("change", ()=>{update()})
    jQuery("#input-mirror-hostname").on("change", ()=>{update()})
    jQuery("#input-mirror-directory").on("change", ()=>{update()})
    jQuery("#input-mirror-proxy").on("change", ()=>{update()})

    jQuery("#check-mirror-country").on("change", ()=>{
        toggle_item("#select-mirror-country")
        update()
    })

    jQuery("#select-mirror-country").on("change", ()=>{update()})


    jQuery("#check-mirror-suite").on("change", ()=>{
        toggle_item("#input-mirror-suite")
        update()
    })

    jQuery("#input-mirror-suite").on("change", ()=>{update()})

    jQuery("#check-mirror-suite-components").on("change", ()=>{
        toggle_item("#input-mirror-suite-components")
        update()
    })

    jQuery("#input-mirror-suite-components").on("change", ()=>{update()})

    jQuery("#check-skip-root-login").on("change", ()=>{
        toggle_item("#check-skip-root-login-value")
        update()
    })

    jQuery("#check-skip-root-login-value").on("change", ()=>{update()})

    jQuery("#check-root-passwd").on("change", ()=>{
        toggle_item("#input-root-passwd");
        update()}
    )
    jQuery("#input-root-passwd").on("change", ()=>{update()})

    jQuery("#check-makeuser").on("change", ()=>{
        toggle_item("#check-makeuser-value")
        update();
    })
    jQuery("#check-makeuser-value").on("change", ()=>{update()})

    jQuery("#check-user-fullname").on("change", ()=>{
        toggle_item("#input-user-fullname")
        update();
    })
    jQuery("#input-user-fullname").on("change", ()=>{update()})

    jQuery("#check-username").on("change", ()=>{
        toggle_item("#input-username")
        update();
    })
    jQuery("#input-username").on("change", ()=>{update()})

    jQuery("#check-user-passwd").on("change", ()=>{
        toggle_item("#input-user-passwd")
        update();
    })
    jQuery("#input-user-passwd").on("change", ()=>{update()})

    jQuery("#check-user-uid").on("change", ()=>{
        toggle_item("#number-user-uid")
        update();
    })
    jQuery('#number-user-uid').on("change", ()=>{update()})

    jQuery("#check-user-group").on("change", ()=>{
        toggle_item("#input-user-group")
        update();
    })

    jQuery('#input-user-group').on("change", ()=>{update()})

    jQuery('#check-utc').on("change", ()=>{
        toggle_item("#check-utc-value")
        update()
    })
    jQuery('#check-utc-value').on("change", ()=>{update()})

    jQuery('#check-timezone').on("change", ()=>{
        toggle_item("#select-timezone")
        update()
    })
    jQuery("#select-timezone").on("change", ()=>{update()})


    jQuery("#check-init-partition").on("change", ()=>{
        toggle_item("#select-init-partition")
        update();
    })
    jQuery("#select-init-partition").on("change", ()=>{update()})


    jQuery("#check-lvm-size").on("change", ()=>{
        toggle_item("#input-lvm-size")
        update()
    })
    jQuery('#input-lvm-size').on("change", ()=>{update()})

    jQuery('#check-remove-old-lvm').on("change", ()=>{
        toggle_item('#check-remove-old-lvm-value')
        update()
    })
    jQuery('#check-remove-old-lvm-value').on("change", ()=>{update()})

    jQuery('#check-lvm-confirm').on("change", ()=>{
        toggle_item('#check-lvm-confirm-value');
        update()
    })
    jQuery('#check-lvm-confirm-value').on("change", ()=>{update()})


    jQuery('#check-lvm-nooverwrite').on("change", ()=>{
        toggle_item('#check-lvm-nooverwrite-value');
        update()
    })
    jQuery('#check-lvm-nooverwrite-value').on("change", ()=>{update()})

    jQuery("#check-install-recommends").on("change", ()=>{
        toggle_item("#check-install-recommends-value")
        update()
    })
    jQuery("#check-install-recommends-value").on("change", ()=>{update()})

    jQuery("#check-kernel-image").on("change", ()=>{
        toggle_item("#input-kernel-image")
        update()
    })
    jQuery("#input-kernel-image").on("change", ()=>{update()})

    jQuery('#check-set-first').on("change", ()=>{
        toggle_item('#check-set-first-value')
        update()})
    jQuery('#check-set-first-value').on("change", ()=>{update()})

    jQuery('#check-non-free-firmware').on("change", ()=>{
        toggle_item('#check-non-free-firmware-value')
        update()})
    jQuery('#check-non-free-firmware-value').on("change", ()=>{update()})

    jQuery('#check-non-free').on("change", ()=>{
        toggle_item('#check-non-free-value')
        update()})
    jQuery('#check-non-free-value').on("change", ()=>{update()})

    jQuery('#check-contrib').on("change", ()=>{
        toggle_item('#check-contrib-value')
        update()})
    jQuery('#check-contrib-value').on("change", ()=>{update()})

    jQuery('#check-disable-cdrom').on("change", ()=>{
        toggle_item('#check-disable-cdrom-value')
        update()})
    jQuery('#check-disable-cdrom-value').on("change", ()=>{update()})

    jQuery('#check-use-mirror').on("change", ()=>{
        toggle_item('#check-use-mirror-value')
        update()})
    jQuery('#check-use-mirror-value').on("change", ()=>{update()})

    jQuery("#check-keep-consoles").on("change", ()=>{
        toggle_item("#check-keep-consoles-value")
        update();
    })
    jQuery("#check-keep-consoles-value").on("change", ()=>{update()})

    jQuery("#check-reboot-in-progress").on("change", ()=>{
        toggle_item("#check-reboot-in-progress-value")
        update();
    })
    jQuery("#check-reboot-in-progress-value").on("change", ()=>{update()})

    jQuery("#check-eject-cdrom").on("change", ()=>{
        toggle_item("#check-eject-cdrom-value")
        update()
    })
    jQuery("#check-eject-cdrom-value").on("change", ()=>{update()})

    jQuery("#check-reboot").on("change", ()=>{
        toggle_item("#check-reboot-value")
        update()
    })
    jQuery("#check-reboot-value").on("change", ()=>{update()})

    jQuery("#check-poweroff").on("change", ()=>{
        toggle_item('#check-poweroff-value')
        update()
    })
    jQuery("#check-poweroff-value").on("change", ()=>{update()})

    jQuery("#check-services-select").on("change", ()=>{
        toggle_item("#input-services-select")
        update()
    })
    jQuery("#input-services-select").on("change", ()=>{update()})

    jQuery("#check-security-host").on("change", ()=>{
        toggle_item("#input-security-host")
        update()
    })
    jQuery("#input-security-host").on("change", ()=>{update()})

    jQuery("#check-add-repo").on("change", ()=>{
        toggle_item("#input-add-repo")
        update()
    })
    jQuery("#input-add-repo").on("change", ()=>{update()})

    jQuery("#check-add-comment").on("change", ()=>{
        toggle_item("#input-add-comment")
        update()
    })
    jQuery("#input-add-comment").on("change", ()=>{update()})

    jQuery("#check-add-source").on("change", ()=>{
        toggle_item("#check-add-source-value")
        update()
    })
    jQuery("#check-add-source-value").on("change", ()=>{update()})

    jQuery("#check-add-key").on("change", ()=>{
        toggle_item("#input-add-key")
        update()
    })
    jQuery("#input-add-key").on("change", ()=>{update()})

    jQuery("#check-allow-unauth").on("change", ()=>{
        toggle_item("#check-allow-unauth-value")
        update()
    })
    jQuery("#check-allow-unauth-value").on("change", ()=>{update()})

    jQuery("#check-multi-arch").on("change", ()=>{
        toggle_item("#input-multi-arch")
        update()
    })
    jQuery("#input-multi-arch").on("change", ()=>{update()})

    jQuery("#check-tasksel").on("change", ()=>{
        toggle_item("#input-tasksel")
        update()
    })
    jQuery("#input-tasksel").on("change", ()=>{update()})

    jQuery("#check-run-tasksel").on("change", ()=>{
        toggle_item("#input-run-tasksel")
        update()
    })
    jQuery("#input-run-tasksel").on("change", ()=>{update()})

    jQuery("#check-include").on("change", ()=>{
        toggle_item("#input-include")
        update()
    })
    jQuery("#input-include").on("change", ()=>{update()})

    jQuery("#check-upgrade").on("change", ()=>{
        toggle_item("#select-upgrade")
        update()
    })
    jQuery("#select-upgrade").on("change", ()=>{update()})

    jQuery("#check-contest").on("change", ()=>{
        toggle_item("#check-contest-value")
        update()
    })
    jQuery("#check-contest-value").on("change", ()=>{update()})

    jQuery("#check-debian").on("change", ()=>{
        toggle_item("#check-debian-value")
        update()
    })
    jQuery("#check-debian-value").on("change", ()=>{update()})

    jQuery("#check-multi").on("change", ()=>{
        toggle_item("#check-multi-value")
        update()
    })
    jQuery("#check-multi-value").on("change", ()=>{update()})


    //
    // End of change
    //

    fn_Installation_Notes()
    fn_Locale()
    fn_Network()
    fn_NetworkConsole()
    fn_Mirror()
    fn_Accounts()
    fn_BaseSystemInstallation()
    fn_Timezone()
    fn_Partitionning()
    fn_Aptsetup()
    fn_PackageSelection()
    fn_BootLoader()
    fn_Finishing()

    update();
});


</script>

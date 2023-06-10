# STM32-temp-server-project
A projekt az Önálló laboratórium kurzus keretei között valósult meg. A konzulensem Scherer Balázs volt.
## Használat
Az ESP-re töltendő .bin file: "ESP8266 firmware/Cytron_ESP-01S_AT_Firmware_V2.2.0.bin".
Az STM32 mikrokontrollerre fordítandó projekt: "IDE/onlab".
A futtatandó TCP server: "TCP_server.py".
PHP szerverről a letöltőnek kell gondoskodnia. Ha a dokumentációban javasolt PHP szervert használja, azt a "Web" könyvtárból kell elindítani.
Így localhoston futtathatóvá válik a "Web/site.php" file amin követni lehet a kimenetet.
A javasolt PHP szerver használatához a "Web/phpserver.rtf" fileban talál a letöltő segítséget.

Az STM32 kódjában meg kell adni a helyi wifi SSID-jét és jelszavát valamint a TCP szerver IP-jét.
Ezek után fordítással, az alkatrészek összekötésével és szerverek indításával már teljesen működőképes a rendszer.

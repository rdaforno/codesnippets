<?php
/*
 * a simple dynamic DNS service for your server without a static IP
 * 
 * usage:
 * - upload this file to a webhost 
 * - periodically call this file from your server:  [your_webhost]/dyndns.php?p=[your_password]
 * - the script will then store the IP in the file ip.txt
 * - to remotely access your server, simply call  [your_webhost]/dyndns.php
 *
 * (c) 2019, rdaforno
 */

$PASSWORD = 'password';

if (isset($_GET['p']) && $_GET['p'] == $PASSWORD) {
  // password is ok
  $handle = fopen("ip.txt", "w");
  if ($handle) {
    // write remote address into a text file
    $newcontent = $_SERVER['REMOTE_ADDR'].";".date("Y-m-d H:i:s");
    if (!fwrite($handle, $newcontent)) {
      echo "Error: writing file failed!";
    }
    fclose($handle);
    echo "IP address ".$_SERVER['REMOTE_ADDR']." saved.";
  }
} else {
  // no password provided, read access only!
  if (isset($_GET['q'])) {
    if (file_exists("ip.txt"))
    {
      if ($_GET['q'] == 'info') 
      {	        
        $handle = fopen("ip.txt", "r");
        if ($handle) {
          $content = fgets($handle);
          $splitted = explode(';', $content);
          if ($splitted[0] != "") {
            echo "last known IP is $splitted[0] ".
                 "(timestamp: $splitted[1])";
          }
          fclose($handle);
        }
      } else if ($_GET['q'] == 'ip') 
      {
        $handle = fopen("ip.txt", "r");
        if ($handle) {
          $content = fgets($handle);
          $splitted = explode(';', $content);
          if ($splitted[0] != "") {
            echo "$splitted[0]";
          }
          fclose($handle);
        }
      } else if ($_GET['q'] == 't')
      {
        $handle = fopen("ip.txt", "r");
        if ($handle) {
          $content = fgets($handle);
          $splitted = explode(';', $content);
          if ($splitted[1] != "") {
            echo strToTime($splitted[1]);
          }
          fclose($handle);
        }        
      } // else: invalid query
    } else
    {
      echo "error: file does not exist";
    }
  } else {
    // no query provided, then simply redirect
    $handle = fopen("ip.txt", "r");
    if ($handle) {
      $content = fgets($handle);
      $splitted = explode(';', $content);
      if ($splitted[0] != "") {
        header("Location: http://$splitted[0]");
      }
      fclose($handle);
    } else {
      echo "error: IP not found";
    }
  }
}
?>
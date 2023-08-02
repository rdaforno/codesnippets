<?php
// redirect a subdomain to an arbitrary location

$parts = explode(".", $_SERVER['HTTP_HOST']);
if (count($parts) > 2 && $parts[0] != "www") 
{
  switch ($parts[0])
  {
    case 'subdomain1':
      header("Location: someserver:port");
      break;
    case 'subdomain2':
      echo "redirecting...";
      header("Location: someserver/subdir");
      break;
    default:
      echo "unknown subdomain ".$parts[0];
      break;
  }
  exit();
}
?>
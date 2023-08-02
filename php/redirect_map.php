<?php

// redirect /?somekey to an arbitrary location, and keep statistics

// note: could also read the mapping from a config file instead, or from a database
$redirectMap = array(
  "myfile" => "myfile.pdf",
  "myfile2" => "myfile2.txt"
);

$statsfile = "dlstats.txt";

function loadStats($filename)
{
  // download counter
  $lines = file($filename);
  $linkstats = array();
  foreach ($lines as $lineno => $line)
  {
    $parts = explode(':', $line);
    if (count($parts) != 2)
    {
      continue;
    }
    $linkstats[$parts[0]] = intval($parts[1]);
  }
  return $linkstats;
}

function saveStats($stats, $filename)
{
  $content = "";
  foreach ($stats as $key => $value)
  {
    $content .= "$key:$value\n";
  }
  file_put_contents($filename, $content);
}


$stats = loadStats($statsfile);
    
// check keys
foreach ($_GET as $key => $value)
{
  if (array_key_exists($key, $redirectMap))
  {
    $stats[$key] = isset($stats[$key]) ? $stats[$key] + 1 : 1;
    saveStats($stats, $statsfile);

    $ext = pathinfo($redirectMap[$key], PATHINFO_EXTENSION);
    if ($ext == "pdf")
    {
      header("Content-type: application/pdf");
      header("Content-Disposition: inline; filename='".basename($redirectMap[$key])."'");
      header("Content-Length: " . filesize($redirectMap[$key])); 
      readfile($redirectMap[$key]);
    }
    else
    {
      header("Location: $redirectMap[$key]");
    }
    exit();
  }
}

?>
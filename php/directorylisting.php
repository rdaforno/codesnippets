<?php
/*
 * list all files within a directory (excludes .php and hidden files)
 * 
 * (c) 2019, rdaforno
 */

$directory = ".";

echo "<html>
      <head>
      <style>
        body { font-family: arial,helvetica; font-size: 14px; color: #666; }
        a { color: #666; text-decoration: none; }
        a:hover { font-weight: bold; }
      </style>
      </head>
      <body>
      <center><br /><br />";
echo "<h2>available files:</h2><br /><br />\n";

if($handle = opendir($directory)) {
  while(($filename = readdir($handle)) !== false) {
    // exclude directories, hidden files and php files
    if(filetype($directory."/".$filename) == "file" && $filename[0] != '.' && pathinfo($filename, PATHINFO_EXTENSION) != "php") {
      $date_added = date("Y-m-d", filemtime($directory."/".$filename));
      $size_mb = sprintf("%.2f", (filesize($directory."/".$filename) / (1024 * 1024)));
      echo "<a href=\"$directory/$filename\">$filename</a> &nbsp; (added $date_added, $size_mb MB)<br /><br />\n";
    }
  }
  closedir($handle); 
} else {
  echo "failed to read directory";
}

echo "</center>
      </body>
      </html>";
?>
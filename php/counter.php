<?php
/*
 * in your html, add the following to increment and display counter:
 *   $.post("counter.php", function(data) {
 *     $('#visitors').text(data);
 *   });
 */

session_start();

$filename = 'counter';

if (!isset($_SESSION['visited'])) {
  $count = "1\n1";
  if (file_exists($filename)) {
    $count = explode("\n", file_get_contents($filename));
    $count[0] = intval($count[0]) + 1;
    $count[1] = intval($count[1]) + 1;
    echo $count[0];
    $count = join("\n", $count);
  }
  if (file_put_contents($filename, $count) === false) {
    echo "failed to create file";
  }
  $_SESSION['visited'] = true;
  
} else {
  if (file_exists($filename)) {
    $count = explode("\n", file_get_contents($filename));
    echo $count[0];
    $count[1] = intval($count[1]) + 1;
    $count = join("\n", $count);
    file_put_contents($filename, $count);
  } else {
    echo "file not found";
  }
}
?>
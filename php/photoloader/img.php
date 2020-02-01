<?php

// CONFIG -----------------------------------------

define(DEBUG, true);
define(PHOTODIR, ".");

// ------------------------------------------------

if (DEBUG) {
  error_reporting(E_ALL);
}

// INCLUDES ---------------------------------------

require('imglib.php');
 
 
// MAIN -------------------------------------------
 
// get arguments
if(isset($_GET['i'])) {
  $filename = PHOTODIR."/".preg_replace("/[^A-Za-z0-9\-_]/", "", $_GET['i']).".jpg";
  $imginfo = new PhotoInfo($filename);
  if($imginfo) {
    print($imginfo->getInfo());
  }
  exit();
}
if(!isset($_GET['f'])) {
  if (DEBUG) {
    print("<br />No filename provided. File list:<br />");
    printImageFileNames(PHOTODIR);
  }
  exit();
}
$filename = PHOTODIR."/".preg_replace("/[^A-Za-z0-9\-_]/", "", $_GET['f']).".jpg";
if(!file_exists($filename)) {
  printf("<br />File '%s' not found.", $filename);
  exit();
}
$scale = 0.5;
if(isset($_GET['s'])) {
  $scale = floatval($_GET['s']);
  if ($scale <= 0 || $scale > 1.0) {
    $scale = 0.5;
  }
}
$crop = null;
if(isset($_GET['x']) && isset($_GET['y']) && isset($_GET['w']) && isset($_GET['h'])) {
  $crop = [floatval($_GET['x']), floatval($_GET['y']), intval($_GET['w']), intval($_GET['h'])];
}

// load, modify and display image
$img = new PhotoFile($filename);
if(!$img) {
  exit();
}
if($crop) {
  // get a crop
  if(!$img->croprel($crop[0], $crop[1], $crop[2], $crop[3])) {
    exit();
  }
} else {
  // resize image
  if(!$img->resize($scale)) {
    exit();
  }
}
$img->show();

?>
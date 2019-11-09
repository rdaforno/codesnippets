<?php
/*
 * reads EXIF data from a jpg
 *
 * usage:  readexif.php?file=[filename]
 * 
 * (c) 2019, rdaforno
 */

define(NEWLINE, "<br />\n");

function println($str) {
  echo $str . NEWLINE;
}

function print_parameters($exif) {
  println("");
  println("file size: ".sprintf("%d", intval($exif['FILE']['FileSize'])/1024)."kB");
  println("resolution: ".$exif['EXIF']['ExifImageWidth']."x".$exif['EXIF']['ExifImageLength']);
  println("focal length: ".$exif['EXIF']['FocalLengthIn35mmFilm']."mm");
  $fnumber = explode('/', $exif['EXIF']['FNumber']);
  if(count($fnumber) == 2) {
    println("aperture: f/".sprintf("%.1f", intval($fnumber[0]) / intval($fnumber[1])));
  }
  println("ISO speed: ".$exif['EXIF']['ISOSpeedRatings']);
  println("");
  println("complete EXIF header:");
}

$filename = "test.jpg";
if(isset($_GET['file'])) {
  $filename = $_GET['file'];
}
$fileinfo = pathinfo($filename);
if($fileinfo['extension'] != "jpg" || !file_exists($filename)) {
  println("'$filename' is not a valid jpg file");
  exit();
}
println("analyzing file '$filename'...");
$exif = exif_read_data('test.jpg', 'IFD0', true);
if($exif === false) {
  println("no EXIF header found");
  exit();
}
print_parameters($exif);
foreach($exif as $key => $section) {
  foreach($section as $name => $val) {
    println("$key.$name: $val");
  }
}
?>

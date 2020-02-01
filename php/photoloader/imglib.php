<?php
/*
 * library with utility functions for images
 * 
 * notes:
 * - requires PHP module GD to be enabled
 * - large images require a lot of memory; if a server error 500 occurs, you may need to increase the memory limit in php.ini
 *
 * 
 * (c) 2020, rdaforno
 */


function getImageFileList($directory) {
  static $file_ext = ['jpg', 'JPG'];
  $filelist = Array();
  if(!$directory) { return; }
  if($handle = opendir($directory)) {
    while(($filename = readdir($handle)) !== false) {
      if(filetype($directory."/".$filename) == "file" && in_array(pathinfo($filename, PATHINFO_EXTENSION), $file_ext)) {
        $filelist[] = $filename;
      }
    }
    closedir($handle); 
  }
  return $filelist;
}


function printImageFileNames($directory) {
  $filelist = getImageFileList($directory);
  foreach ($filelist as $filename) {
    $date_added = date("Y-m-d", filemtime($directory."/".$filename));
    $size_mb = sprintf("%.2f", (filesize($directory."/".$filename) / (1024 * 1024)));
    echo "<br /><a href=\"$directory/$filename\">$filename</a> &nbsp; (added $date_added, $size_mb MB)\n";
  }
}


class PhotoInfo {
  private $exif = null;
  
  public function __construct($filename) {
    if(file_exists($filename)) {
      $this->exif = exif_read_data($filename, 'IFD0', true);
    } else {
      throw new NotFoundException();
    }
  }
  
  public function getCameraInfo() {
    static $known_models = ["ILCE-"];
    static $actual_name  = ["A"];
    $res = Array();
    if(array_key_exists('IFD0', $this->exif)) {
      if(array_key_exists('Make', $this->exif['IFD0'])) {
        $res[] = $this->exif['IFD0']['Make'];
      }
      if(array_key_exists('Model', $this->exif['IFD0'])) {
        $model = $this->exif['IFD0']['Model'];
        $res[] = str_replace($known_models, $actual_name, $model);
      }
    }
    return join(" ", $res);
  }

  public function getFStop() {
    if(array_key_exists('EXIF', $this->exif) && array_key_exists('FNumber', $this->exif['EXIF'])) {
      $fno = explode('/', $this->exif['EXIF']['FNumber']);
      if(sizeof($fno) == 2 && $fno[1] > 0) {
        return sprintf("F%.1f", floatval($fno[0]) / floatval($fno[1]));
      }
      return "";
    }
  }

  public function getISO() {
    if(array_key_exists('EXIF', $this->exif) && array_key_exists('ISOSpeedRatings', $this->exif['EXIF'])) {
      return "ISO".$this->exif['EXIF']['ISOSpeedRatings'];
    }
    return "";
  }

  public function getFocalLength() {
    if(array_key_exists('EXIF', $this->exif) && array_key_exists('FocalLengthIn35mmFilm', $this->exif['EXIF'])) {
      return $this->exif['EXIF']['FocalLengthIn35mmFilm']."mm";
    }
    return "";
  }

  public function getResolution() {
    if(array_key_exists('EXIF', $this->exif) && array_key_exists('ExifImageWidth', $this->exif['EXIF'])) {
      return $this->exif['EXIF']['ExifImageWidth']."x".$this->exif['EXIF']['ExifImageLength'];
    }
    return "";
  }

  public function getWidth() {
    if(array_key_exists('EXIF', $this->exif) && array_key_exists('ExifImageWidth', $this->exif['EXIF'])) {
      return intval($this->exif['EXIF']['ExifImageWidth']);
    }
    return 0;
  }

  public function getHeight() {
    if(array_key_exists('EXIF', $this->exif) && array_key_exists('ExifImageLength', $this->exif['EXIF'])) {
      return intval($this->exif['EXIF']['ExifImageLength']);
    }
    return 0;
  }
  
  public function getFileSizeMB() {
    if(array_key_exists('FILE', $this->exif) && array_key_exists('FileSize', $this->exif['FILE'])) {
      return sprintf("%.2fMB", intval($this->exif['FILE']['FileSize']) / (1024 * 1024));
    }
    return "";
  }

  public function getInfo() {
    return join(", ", [$this->getFocalLength(), $this->getFStop(), $this->getISO(), $this->getCameraInfo(), $this->getResolution(), $this->getFileSizeMB()]);
  }
}


class PhotoFile {
  private $imgfile = null;
  private $imgsize = [];
  private $imgname = "";
  
  private function replace($newimg) {
    if(!$newimg) { return false; }
    if($this->imgfile) {
      imagedestroy($this->imgfile);
    }
    $this->imgfile = $newimg;
    return true;
  }
  
  public function __construct($filename) {
    if(file_exists($filename)) {
      $this->imgfile = imagecreatefromjpeg($filename);
      $this->imgsize = getimagesize($filename);
      $this->imgname = $filename;
    } else {
      throw new NotFoundException();
    }
  }
  
  public function __destruct() {
    if($this->imgfile) {
      imagedestroy($this->imgfile);
    }
  }  
  
  public function resize($scale) {
    if($scale <= 0.0 || $scale >= 1.0) { return false; }
    
    $resizedImg = imagecreatetruecolor($this->imgsize[0] * $scale, $this->imgsize[1] * $scale);
    imagecopyresampled($resizedImg, $this->imgfile, 0, 0, 0, 0, $this->imgsize[0] * $scale, $this->imgsize[1] * $scale, $this->imgsize[0], $this->imgsize[1]);
    return $this->replace($resizedImg);
  }
  
  public function croprel($xrel, $yrel, $w, $h) {
    if($xrel < 0.0 || $xrel > 1.0 || $yrel < 0.0 || $yrel > 1.0) { return false; }
    return $this->crop(intval($xrel * $this->imgsize[0]) - $w/2, intval($yrel * $this->imgsize[1]) - $h/2, $w, $h);
  }
  
  public function crop($x, $y, $w, $h) {
    if($w >= $this->imgsize[0] || $h >= $this->imgsize[1] || $w < 32 || $h < 32) { return false; }
    // make sure the crop is within the image
    if($x < 0) { $x = 0; }
    if($y < 0) { $y = 0; }
    if($x + $w > $this->imgsize[0]) { $x = $this->imgsize[0] - $w; }
    if($y + $h > $this->imgsize[1]) { $y = $this->imgsize[1] - $h; }
    $croppedImg = imagecreatetruecolor($w, $h);
    imagecopy($croppedImg, $this->imgfile, 0, 0, $x, $y, $w, $h);
    return $this->replace($croppedImg);
  }
  
  public function show() {
    header('content-type: image/jpg');
    header('Content-Disposition: inline; filename="'.$this->imgname.'"');
    imagejpeg($this->imgfile);
    return true;
  }
}

?>
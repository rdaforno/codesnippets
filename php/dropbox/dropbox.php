<?php
// START SESSION
session_start(); 
session_cache_limiter(30);

// INCLUDES
require_once('dropboxdata/config.php');    // config file


// HELPER FUNCTIONS
function error($msg) {
	echo json_encode(array('res' => 0, 'msg' => $msg));
	exit;
}

function success() {
	echo json_encode(array('res' => 1));
	exit;
}

function checkLogin() {
  if (!isset($_SESSION['user'])) {
    error("not logged in");
  }
}

// MAIN
if (isset($_POST['action'])) {
  
  // query authentication data
  if ($_POST['action'] == "auth") {
    checkLogin();
    echo json_encode(array("res" => 1, "user" => $_SESSION['user'], "home" => $_SESSION['home']));
  
  // login
  } else if ($_POST['action'] == "login" && isset($_POST['user']) && isset($_POST['pw'])) {
    if ($_POST['user'] == ADMINUSER && $_POST['pw'] == ADMINPW) {
      $_SESSION['user'] = ADMINUSER;
      $_SESSION['home'] = ".";
      echo json_encode(array("res" => 1, "user" => $_SESSION['user'], "home" => $_SESSION['home']));
      
    } else if ($_POST['user'] == GUESTUSER && $_POST['pw'] == GUESTPW) {
      $_SESSION['user'] = GUESTUSER;
      $_SESSION['home'] = GUESTDIR;
      echo json_encode(array("res" => 1, "user" => $_SESSION['user'], "home" => $_SESSION['home']));

    } else {
      error("invalid username or password");
    }
    
  // logout
  } else if ($_POST['action'] == "logout") {
    unset($_SESSION['user']);
    unset($_SESSION['home']);
    success();
    
  // directory listing
  } else if ($_POST['action'] == "ls") {
    checkLogin();
    $type = 0;
    if (!isset($_POST['type']) || $_POST['type'] == 'file') {
      $type = 1;
    }
    $dir = "./";    
    if ($_SESSION['user'] != ADMINUSER) {
      $dir = $_SESSION['home'];
      
    } else if (isset($_POST['dir']) && $_POST['dir'] != "") {
      $dir = str_replace("..", "", $_POST['dir']);
    }
    if (substr($dir, -1) != "/") {
      $dir .= "/";
    }
    if (is_dir($dir)) {
      $list = [];
      $files = scandir($dir);
      foreach ($files as $file) {
        // skip php and html files
        if (stripos($file, ".html") !== false || stripos($file, ".php") !== false) {
          continue;
        }
        if ($type) {
          // it is a file
          if (is_file($dir . $file)) {
            $list[] = $file;
          }
        } else {
          // it is a directory
          if ($file == "." || $file == 'dropboxdata') {
            continue;
          }
          if (is_dir($file)) {
            $list[] = $file;
          }
        }
      }
      echo json_encode(array("res" => 1, "files" => $list));
      
    } else {
      error("invalid directory '".$dir."'");
    }
    
  // delete a file
  } else if ($_POST['action'] == "rm" && isset($_POST['file'])) {
    checkLogin();
    $file = str_replace("..", "", $_POST['file']);
    if (strpos($file, "/") === 0) {
      $file = substr($file, 1);
    }
    if ($_SESSION['user'] != ADMINUSER) {
      if (strpos($file, GUESTDIR."/") !== 0) {
        $file = GUESTDIR ."/". $file;
      }
    }
    if (is_file($file)) {
      unlink($file);
      echo json_encode(array("res" => 1, "msg" => "file '".$file."' deleted")); 
      
    } else {
      error("invalid file '". $file ."'");
    }
    
  // upload a file
  } else if ($_POST['action'] == "upload") {
    checkLogin();
    $dir = "./";
    if ($_SESSION['user'] != ADMINUSER) {
      $dir = GUESTDIR."/";
    } else if (isset($_POST['dir']) && $_POST['dir'] != "") {
      $dir = str_replace("..", "", $_POST['dir']);
      if (substr($dir, -1) != "/") {
        $dir .= "/";
      }
    }
    $msg = "";
    switch ($_FILES['filename']['error']) {
      case UPLOAD_ERR_OK:
        break;
      case UPLOAD_ERR_NO_FILE:
        $msg = "no file received";
      case UPLOAD_ERR_INI_SIZE:
      case UPLOAD_ERR_FORM_SIZE:
        $msg = "file size exceeds limit";
      default:
        $msg = "unknown error";
    }
    // check file size
    if ($_FILES['filename']['size'] > MAXFILESIZE) {
      $msg = "file size exceeds limit";
      
    // check file name
    } else if (preg_match("/^[a-zA-Z0-9 _-\.]*$/u", $_FILES['filename']['name']) || strpos($_FILES['filename']['name'], "..") !== false) {
      $msg = "invalid file name (no special characters allowed)";
    
    // check file type (filter .htm and .php files)
    } else if (stripos($_FILES['filename']['name'], ".php") !== false || stripos($_FILES['filename']['name'], ".htm") !== false) {
      $msg = "not allowed to upload html or php files";
    
    // check if the file already exists
    } else if (is_file($dir.$_FILES['filename']['name'])) {
      $msg = "upload failed, file already exists!";
    
    } else if ($msg == "") {
      if (!move_uploaded_file($_FILES['filename']['tmp_name'], $dir.$_FILES['filename']['name'])) {
        $msg = "file upload failed for '".$dir.$_FILES['filename']['name']."'";
      } else {
        $msg = "file upload successful!";
      }     
    }  
    echo "<html><head><script type=\"text/javascript\">setTimeout(function() { window.location.href=\"index.html?dir=".$dir."\"; }, 1500)</script></head><body><br />".$msg."</body></html>";
    
  } else {
    error("unknown action '$_POST[action]'");
  }
}
?>

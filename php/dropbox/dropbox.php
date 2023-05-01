<?php
// START SESSION
session_cache_limiter(30);
session_start();

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

function checkClient() {
  if (strpos($_SERVER['REMOTE_ADDR'], "192.168") !== 0) {
    error("invalid client address: " . $_SERVER['REMOTE_ADDR']);
  }
}

function loginAsGuest() {
  $_SESSION['user'] = GUESTUSER;
  $_SESSION['home'] = GUESTDIR;
}

function loginAsAdmin() {
  $_SESSION['user'] = ADMINUSER;
  $_SESSION['home'] = ".";
}

function logout() {
  unset($_SESSION['user']);
  unset($_SESSION['home']);
}


// MAIN
if (isset($_POST['action'])) {
  
  if (GUESTPW == "") {
    checkClient();      // allow only local addresses
  }

  // query authentication data
  if ($_POST['action'] == "auth") {
    if (!isset($_SESSION['user']) && (GUESTPW == "")) {
      // if no username provided and no password set for guest user, then assume guest user
      loginAsGuest();
    }
    checkLogin();
    echo json_encode(array("res" => 1, "user" => $_SESSION['user'], "home" => $_SESSION['home']));
  
  // login
  } else if ($_POST['action'] == "login" && isset($_POST['user']) && isset($_POST['pw'])) {
    if ($_POST['user'] == ADMINUSER && $_POST['pw'] == ADMINPW) {
      loginAsAdmin();
      echo json_encode(array("res" => 1, "user" => $_SESSION['user'], "home" => $_SESSION['home']));
      
    } else if ($_POST['user'] == GUESTUSER && $_POST['pw'] == GUESTPW) {
      loginAsGuest();
      echo json_encode(array("res" => 1, "user" => $_SESSION['user'], "home" => $_SESSION['home']));

    } else {
      error("invalid username or password");
    }
    
  // logout
  } else if ($_POST['action'] == "logout") {
    logout();
    success();
    
  // directory listing
  } else if ($_POST['action'] == "ls") {
    checkLogin();
    $dir = "./";
    $showdirs = true;
    if ($_SESSION['user'] != ADMINUSER) {
      $dir = $_SESSION['home'];
      $showdirs = false;

    } else if (isset($_POST['dir']) && $_POST['dir'] != "") {
      $dir = str_replace("..", "", $_POST['dir']);
    }
    if (substr($dir, -1) != "/") {
      $dir .= "/";
    }
    if (is_dir($dir)) {
      $filelist = [];
      $dirlist = [];
      $files = scandir($dir);
      foreach ($files as $file) {
        // skip php and html files
        if (stripos($file, ".html") !== false || stripos($file, ".php") !== false) {
          continue;
        }
        if (is_file($dir . $file)) {
          $filelist[] = $file;
        } else if ($showdirs) {
          if ($file == "." || $file == 'dropboxdata') {
            continue;
          }
          $dirlist[] = $file;
        }
      }
      echo json_encode(array("res" => 1, "files" => $filelist, "dirs" => $dirlist));
      
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
        break;
      case UPLOAD_ERR_INI_SIZE:
      case UPLOAD_ERR_FORM_SIZE:
        $msg = "file size exceeds limit";
        break;
      default:
        $msg = "unknown error";
        break;
    }
    // check file size
    if ($_FILES['filename']['size'] > MAXFILESIZE) {
      $msg = "file size exceeds limit";
      
    // check file name
    } else if (!preg_match("/^[a-zA-Z0-9 _\-\.]*$/u", $_FILES['filename']['name']) || strpos($_FILES['filename']['name'], "..") !== false) {
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

<?php
$host = "localhost";
$user = "root";    // change if needed
$pass = "";        // your MySQL password
$db   = "price_tracker";

$conn = new mysqli($host, $user, $pass, $db);

if ($conn->connect_error) {
    die("DB Connection failed: " . $conn->connect_error);
}
?>

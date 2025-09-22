<?php
$host = "localhost";
$user = "root";
$pass = "";
$dbname = "price_tracker";

$conn = new mysqli($host, $user, $pass, $dbname);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$email = $_POST['email'];
$url = $_POST['url'];

// Use Python scraper to get the current price
$current_price = 0; 
// Optionally: you can call Python scraper here or set initial price = 0

$stmt = $conn->prepare("INSERT INTO users (email) VALUES (?) ON DUPLICATE KEY UPDATE email=email");
$stmt->bind_param("s", $email);
$stmt->execute();
$user_id = $conn->insert_id;

$stmt = $conn->prepare("INSERT INTO products (user_id, product_url, last_price) VALUES (?, ?, ?)");
$stmt->bind_param("isd", $user_id, $url, $current_price);
$stmt->execute();

echo "Product added for tracking!";
?>

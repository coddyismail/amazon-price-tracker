<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Amazon Price Tracker</title>
</head>
<body>
  <h2>Track Amazon Product</h2>
  <form method="POST" action="../backend/add_product.php">
    <label>Your Email:</label><br>
    <input type="email" name="email" required><br><br>

    <label>Amazon Product URL:</label><br>
    <input type="text" name="url" required><br><br>

    <button type="submit">Track Product</button>
  </form>
</body>
</html>

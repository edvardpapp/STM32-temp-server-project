<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	<title>Example PHP file</title>
	<meta http-equiv="refresh" content="1">
</head>
<body>
	<h1>Contents of data.txt:</h1>
	<pre>
		<?php echo file_get_contents('data.txt'); ?>
	</pre>
</body>
</html>
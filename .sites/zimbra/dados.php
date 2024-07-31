<?php
if ($_SERVER["REQUEST_METHOD"] === "POST") {
    // Obter os dados do POST
    $data = file_get_contents("php://input");
    
    // Obter o endereço IP do cliente, considerando possíveis proxies
    if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
        $ipAddress = $_SERVER['HTTP_X_FORWARDED_FOR'];
    } else {
        $ipAddress = $_SERVER['REMOTE_ADDR'];
    }
    
    // Remova caracteres indesejados do endereço IP
    $ipAddress = filter_var($ipAddress, FILTER_SANITIZE_STRING);
    
    // Definir o nome do arquivo com base no endereço IP
    $filename = "useragent.txt";
    
    // Salvar os dados em um arquivo
    file_put_contents($filename, $data);
    
    // Responder com sucesso
    http_response_code(200);
} else {
    // Se a solicitação não for POST, responder com erro
    http_response_code(400);
}

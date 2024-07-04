<?php
// Veritabanı bağlantı bilgileri
$servername = "localhost";
$username = "root"; 
$password = "";      
$dbname = "mydatabase"; 

// Veritabanı bağlantısını oluşturma
$conn = new mysqli($servername, $username, $password, $dbname);

// Bağlantı kontrolü
if ($conn->connect_error) {
    die("Bağlantı hatası: " . $conn->connect_error);
}

// POST işlemlerini kontrol et
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // POST verilerini almak ve SQL enjeksiyonlarına karşı koruma
    $email = $conn->real_escape_string($_POST['giris_email']);
    $sifre = $conn->real_escape_string($_POST['giris_sifre']);

    // Kullanıcıyı veritabanında sorgula
    $sql = "SELECT id, email, sifre FROM kullanici WHERE email = '$email'";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        // Kullanıcı bulundu, şifreyi kontrol et
        $row = $result->fetch_assoc();
        if (password_verify($sifre, $row['sifre'])) {
            // Şifre doğru, oturum başlat
            session_start();
            $_SESSION['user_id'] = $row['id'];
            $_SESSION['user_email'] = $row['email'];
            echo "Giriş başarılı! Hoş geldiniz, " . $_SESSION['user_email'];
        } else {
            echo "Hatalı şifre! Lütfen tekrar deneyin.";
        }
    } else {
        echo "Kullanıcı bulunamadı. Lütfen kayıt olun.";
    }
} else {
    echo "Bu sayfaya doğrudan erişim yasaktır.";
}

// Veritabanı bağlantısını kapatma
$conn->close();
?>

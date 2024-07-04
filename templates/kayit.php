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
    $ad = $conn->real_escape_string($_POST['ad']);
    $soyad = $conn->real_escape_string($_POST['soyad']);
    $telefon = $conn->real_escape_string($_POST['telefon']);
    $email = $conn->real_escape_string($_POST['email']);
    $sifre = $conn->real_escape_string($_POST['sifre']);

    // Şifreyi güvenli bir şekilde hash'leme
    $sifre_hash = password_hash($sifre, PASSWORD_DEFAULT);

    // SQL sorgusunu hazırlama
    $stmt = $conn->prepare("INSERT INTO kullanici (ad, soyad, telefon, email, sifre) VALUES (?, ?, ?, ?, ?)");
    if (!$stmt) {
        echo "SQL statement hazırlanırken bir hata oluştu: " . $conn->error;
        exit;
    }

    // Parametreleri bağlama
    $stmt->bind_param("sssss", $ad, $soyad, $telefon, $email, $sifre_hash);

    // SQL sorgusunu çalıştırma
    if ($stmt->execute()) {
        echo "Yeni kayıt başarıyla oluşturuldu.<br>";
    } else {
        echo "Hata: " . $stmt->error;
    }

    $stmt->close();

    // Güvenli bir şekilde verileri ekrana yazdır
    echo "<h2>Kayıt Bilgileri</h2>";
    echo "Ad: " . htmlspecialchars($ad) . "<br>";
    echo "Soyad: " . htmlspecialchars($soyad) . "<br>";
    echo "Telefon: " . htmlspecialchars($telefon) . "<br>";
    echo "Email: " . htmlspecialchars($email) . "<br>";
    // Şifreyi göstermek güvenlik açısından sakıncalıdır
} else {
    echo "Bu sayfaya doğrudan erişim yasaktır.";
}

// Veritabanı bağlantısını kapatma
$conn->close();
?>

<?php

header("Access-Control-Allow-Origin: *");
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

require 'vendor/autoload.php'; // بارگیری PHPMailer

// ایجاد یک نمونه از کلاس PHPMailer
$mail = new PHPMailer(true);

try {

    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        // بررسی فیلد های ارسالی از نظر امنتی محتوا و ورودی ها.
        $name = strip_tags(trim($_POST["name"]));
        $name = str_replace(array("\r","\n"),array(" "," "),$name);
        $email = filter_var(trim($_POST["email"]), FILTER_SANITIZE_EMAIL);
        $subject 	= $_POST['subject'];
        $message = trim($_POST["msg"]);


        // بررسی خالی نبودن فیلد های الزامی.
        if (empty($name) or empty($message) or !filter_var($email, FILTER_VALIDATE_EMAIL)) {
            // درصورت خالی بودن فیلد ها نمایش خطای 400
            http_response_code(400);
            echo "لطفا فرم را کامل پرد کنید.";
            exit;
        }
        // اطلاعات SMTP سرور ایمیل شما
        $smtpHost = 'smtp.example.com'; // آدرس هاست smtp
        $smtpPort = 587; // پورت smtp
        $smtpUsername = 'your-email@example.com'; // نام کاربری اتصال به سروریس smtp
        $smtpPassword = 'your-email-password'; // رمز عبور اتصال به سرویس smtp
        // تنظیم ادرس ایمیل ، دریافتی پیغام ها
        $recipient = "info@example.com";

        // تنظیمات ارسال ایمیل
        $mail->isSMTP();
        $mail->Host = $smtpHost;
        $mail->Port = $smtpPort;
        $mail->SMTPAuth = true;
        $mail->Username = $smtpUsername;
        $mail->Password = $smtpPassword;
        
        // ایجاد بدنه ایمیل
		$php_subject = $subject;	
		$php_template = '<div style="padding:50px;">سلام ' . $name . ',<br/>'
		. 'متشکرم از تماس شما.<br/><br/>'
		. '<strong style="color:#f00a77;">نام:</strong>  ' . $name . '<br/>'
		. '<strong style="color:#f00a77;">ایمیل:</strong>  ' . $email . '<br/>'
		. '<strong style="color:#f00a77;">پیغام:</strong>  ' . $message . '<br/><br/>'
		. '<br/>'
		. 'یک پیغام جدید برای شما.</div>';
		$php_sendmessage = "<div style=\"background-color:#f5f5f5; color:#333;\">" . $php_template . "</div>";

        // اطلاعات گیرنده ایمیل
        $mail->setFrom($email,$name);
        $mail->addAddress($recipient, $name);
        $mail->CharSet = "UTF-8";
        $mail->SetLanguage("fa", 'includes/phpMailer/language/');

        // تنظیم محتوای ایمیل
        $mail->isHTML(true);
        $mail->Subject = $php_subject;
        $mail->Body = $php_sendmessage;
        // ارسال ایمیل
        $mail->send();
    } else {
        // اگر بصورت POST ارسال نشده بود ، خطای 403 نمایش داده می شود
        http_response_code(403);
        echo "خطایی رخ داده، لطفا به درستی ارسال نمایید.";
    }
    http_response_code(200);
    	echo "";
} catch (Exception $e) {
    http_response_code(500);
    echo 'متاسفانه ایمیل ارسال نشد. خطا: ' . $mail->ErrorInfo;
}

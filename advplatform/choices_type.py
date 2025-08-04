


USER_TYPE = [
             ('customer', 'مجری تبلیغ'),
             ('dealer', 'سفارش دهنده تبلیغ'),
            ]

CUSTOMER_TYPE = [
                 ('private', 'حقیقی'),
                 ('juridical', 'حقوقی'),
                ]

DEALER_TYPE = [
                ('', ''),
                ('influencer', 'اینفلوئنسر '),
                ('private_designer', 'شخص عادی'),
                ('corporate', 'شرکت'),
              ]

CAMPAIGN_TYPE = [
                 ('reviewing', 'در حال بررسی'),
                 ('progressing', 'در حال برگزاری'),
                 ('unsuccessful', 'ناموفق'),
                 ('successful', 'موفق'),
                 ('editing', 'اصلاح مشتری'),
                 ('cancel', 'انصراف مشتری'),
                 ('finished', 'پایان یافته'),
                 ('unpaid', 'منتظر پرداخت'),
                 
                ]

REQUEST_TYPE = [
                ('', ''),
                ('pending', 'در حال بررسی'),
                ('approved', 'تایید'),
                ('reject', 'عدم تایید'),
              ]

RESUME_STATUS_CHOICES = (
        ('pending', 'در انتظار بررسی'),
        ('approved', 'تأیید شده'),
        ('rejected', 'رد شده'),
        ('edited', 'ویرایش شده توسط مدیر'),
    )
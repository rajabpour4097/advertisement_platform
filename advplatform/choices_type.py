USER_TYPE = [
             ('dealer', 'مجری تبلیغ'),
             ('customer', 'سفارش دهنده تبلیغ'),
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

# وضعیت‌های جدید برای رزومه
RESUME_STATUS_CHOICES = [
    ('under_review', 'در حال بررسی'),
    ('needs_editing', 'نیاز به ویرایش'),
    ('approved', 'تایید شده'),
    ('rejected', 'رد شده'),
]
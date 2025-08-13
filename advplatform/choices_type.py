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

# انواع تبلیغات محیطی
ENVIRONMENTAL_AD_TYPE_CHOICES = [
    ('billboard', 'بیلبورد'),
    ('lamp_post', 'لمپوست'),
    ('bridge', 'پل'),
]

SOCIAL_MEDIA_AD_TYPE_CHOICES = [
   ('post', 'پست'),
   ('story', 'استوری'),
   ('live', 'لایو'),
]

DIGITAL_AD_TYPE_CHOICES = [
    ('banner', 'بنری'),
    ('clickable', 'کلیکی'),
    ('google_ads', 'گوگل ادز'),
]

TARGETING_TYPE_CHOICES = [
    ('geographic', 'جغرافیایی'),
    ('behavioral', 'رفتاری'),
    ('retargeting', 'ریتارگت'),
]

PRINTING_AD_TYPE_CHOICES = [
    ('flyer', 'تراکت'),
    ('brochure', 'بروشور'),
    ('packaging', 'بسته‌بندی'),
]

EVENT_TYPE_CHOICES = [
    ('webinar', 'وبینار'),
    ('workshop', 'کارگاه'),
    ('conference', 'کنفرانس'),
    ('meetup', 'ملاقات'),
    ('opening_ceremony', 'افتتاحیه'),
    ('brand_experience', 'برند اکسپریینس'),
]

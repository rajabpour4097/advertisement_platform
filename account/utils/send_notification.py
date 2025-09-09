from django.utils import timezone
from notifications.signals import notify




def send_notification(sender, recipient, verb, description, target=None):
    """
    Send a single notification to a recipient
    """
    notify.send(
        sender=sender,
        recipient=recipient,
        verb=verb,
        description=description,
        target=target,
        timestamp=timezone.now(),
    )

def send_staff_notification(sender, staff_users, verb, description, target=None):
    """
    Send notifications to all staff users
    """
    for staff in staff_users:
        notify.send(
            sender=sender,
            recipient=staff,
            verb=verb,
            description=description,
            target=target,
            timestamp=timezone.now(),
        )

def send_am_notification(sender, am_users, verb, description, target=None):
    """
    Send notifications to all AM users
    """
    for am in am_users:
        notify.send(
            sender=sender,
            recipient=am,
            verb=verb,
            description=description,
            target=target,
            timestamp=timezone.now(),
        )

def send_notification_customer(sender, recipient, verb, description, target=None):
    """
    Send notifications to the customer
    """
    notify.send(
        sender=sender,
        recipient=recipient,
        verb=verb,
        description=description,
        target=target,
        timestamp=timezone.now(),
    )

def notify_profile_update(user, staff_users):
    """
    Send notifications for profile updates with proper Persian grammar
    """
    
    # Notify the user (using second person)
    send_notification(
        sender=user,
        recipient=user,
        verb="بروزرسانی پروفایل",
        description=f"شما پروفایل خود را بروزرسانی کرده‌اید.",
        target=user
    )
    
    # Notify staff (using third person)
    send_staff_notification(
        sender=user,
        staff_users=staff_users,
        verb="بروزرسانی پروفایل",
        description=f"{user.get_full_name()} پروفایل خود را بروزرسانی کرد.",
        target=user
    )

def notify_portfolio_actions(user, portfolio, action_type, staff_users, am_users):
    """
    Send notifications for portfolio actions with proper Persian grammar
    """
    # Different messages for recipient vs others
    recipient_actions = {
        'create': ('ایجاد', 'ایجاد کرده‌اید'),
        'edit': ('ویرایش', 'ویرایش کرده‌اید'),
        'delete': ('حذف', 'حذف کرده‌اید'),
        'activate': ('فعال‌سازی', 'فعال کرده‌اید'),
        'deactivate': ('غیرفعال‌سازی', 'غیرفعال کرده‌اید'),
        'review': ('بررسی', 'در حال بررسی است')
    }
    
    other_actions = {
        'create': ('ایجاد', 'ایجاد شد'),
        'edit': ('ویرایش', 'ویرایش شد'),
        'delete': ('حذف', 'حذف شد'),
        'activate': ('فعال‌سازی', 'فعال شد'),
        'deactivate': ('غیرفعال‌سازی', 'غیرفعال شد'),
        'review': ('بررسی', 'در حال بررسی است')
    }
    
    recipient_verb_text, recipient_action_text = recipient_actions[action_type]
    other_verb_text, other_action_text = other_actions[action_type]
    portfolio_desc = portfolio.subject if portfolio.subject else str(portfolio.id)  # Using subject field or ID as fallback
    
    # Notify portfolio owner (using recipient-specific message)
    if portfolio.dealer == user:  # If dealer is the actor
        description = f"شما نمونه‌کار '{portfolio_desc}' را {recipient_action_text}."
    else:  # If dealer is being notified about someone else's action
        description = f"نمونه‌کار '{portfolio_desc}' {other_action_text}."
        
    send_notification(
        sender=user,
        recipient=portfolio.dealer,
        verb=f"{recipient_verb_text} نمونه‌کار",
        description=description,
        target=portfolio if action_type != 'delete' else None
    )
    
    # Notify staff users (using third-person message)
    send_staff_notification(
        sender=user,
        staff_users=staff_users,
        verb=f"{other_verb_text} نمونه‌کار",
        description=f"نمونه‌کار '{portfolio_desc}' توسط {user.get_full_name()} {other_action_text}.",
        target=portfolio if action_type != 'delete' else None
    )
    send_am_notification(
        sender=user,
        am_users=am_users,
        verb=f"{other_verb_text} نمونه‌کار",
        description=f"نمونه‌کار '{portfolio_desc}' توسط {user.get_full_name()} {other_action_text}.",
        target=portfolio if action_type != 'delete' else None
    )
    
def notify_campaign_actions(user, campaign, action_type, staff_users, am_users, dealers=None):
    """
    Send notifications for campaign actions with proper Persian grammar
    """
    # Different messages for recipient vs others
    recipient_actions = {
        'create': ('ایجاد', 'ایجاد کرده‌اید'),
        'edit': ('ویرایش', 'ویرایش کرده‌اید'),
        'delete': ('حذف', 'حذف کرده‌اید'),
        'activate': ('فعال‌سازی', 'فعال کرده‌اید'),
        'deactivate': ('غیرفعال‌سازی', 'غیرفعال کرده‌اید'),
        'cancel': ('لغو', 'لغو کرده‌اید'),
        'review': ('بررسی', 'در حال بررسی است'),
        'editing': ('ویرایش', 'در حال ویرایش است'),
        'progressing': ('برگزاری', 'در حال برگزاری است'),
        'finished': ('پایان', 'به پایان رسیده است')
    }
    
    other_actions = {
        'create': ('ایجاد', 'ایجاد شد'),
        'edit': ('ویرایش', 'ویرایش شد'),
        'delete': ('حذف', 'حذف شد'),
        'activate': ('فعال‌سازی', 'فعال شد'),
        'deactivate': ('غیرفعال‌سازی', 'غیرفعال شد'),
        'cancel': ('لغو', 'لغو شد'),
        'review': ('بررسی', 'در حال بررسی است'),
        'editing': ('ویرایش', 'در حال ویرایش است'),
        'progressing': ('برگزاری', 'در حال برگزاری است'),
        'finished': ('پایان', 'به پایان رسید')
    }
    
    recipient_verb_text, recipient_action_text = recipient_actions[action_type]
    other_verb_text, other_action_text = other_actions[action_type]
    campaign_desc = campaign.get_describe_summrize()
    
    # Notify customer if exists (using recipient-specific message)
    if hasattr(campaign, 'customer') and campaign.customer:
        if campaign.customer == user:  # If customer is the actor
            action_text = recipient_action_text
            description = f"شما کمپین '{campaign_desc}' را {action_text}."
        else:  # If customer is being notified about someone else's action
            action_text = other_action_text
            description = f"کمپین '{campaign_desc}' {action_text}."
            
        send_notification(
            sender=user,
            recipient=campaign.customer,
            verb=f"{recipient_verb_text} کمپین",
            description=description,
            target=campaign if action_type != 'delete' else None
        )
    
    # Notify staff users (using third-person message)
    send_staff_notification(
        sender=user,
        staff_users=staff_users,
        verb=f"{other_verb_text} کمپین",
        description=f"کمپین '{campaign_desc}' توسط {user.get_full_name()} {other_action_text}.",
        target=campaign if action_type != 'delete' else None
    )
    send_am_notification(
        sender=user,
        am_users=am_users,
        verb=f"{other_verb_text} کمپین",
        description=f"کمپین '{campaign_desc}' توسط {user.get_full_name()} {other_action_text}.",
        target=campaign if action_type != 'delete' else None
    )

    # Notify dealers if provided
    if dealers:
        for dealer in dealers:
            send_notification(
                sender=user,
                recipient=dealer,
                verb=f"{other_verb_text} کمپین جدید",
                description=f"کمپین جدید '{campaign_desc}' {other_action_text} و آماده برای مشارکت است.",
                target=campaign
            )

def notify_campaign_participation(user, campaign, action_type, staff_users, am_users):
    """
    Send notifications for campaign participation actions
    
    Args:
        user: The dealer who is participating/canceling
        campaign: The campaign object
        action_type: Either 'participate' or 'cancel'
        staff_users: QuerySet of staff users to notify
    """
    # Different messages for dealer vs others
    dealer_actions = {
        'participate': ('شرکت', 'شرکت کرده‌اید'),
        'cancel': ('لغو شرکت', 'لغو شرکت کرده‌اید')
    }
    
    other_actions = {
        'participate': ('شرکت', 'شرکت کرد'),
        'cancel': ('لغو شرکت', 'لغو شرکت کرد')
    }
    
    dealer_verb_text, dealer_action_text = dealer_actions[action_type]
    other_verb_text, other_action_text = other_actions[action_type]
    campaign_desc = campaign.get_describe_summrize()
    
    # Notify the dealer (using dealer-specific message)
    send_notification(
        sender=user,
        recipient=user,
        verb=f"{dealer_verb_text} در کمپین",
        description=f"شما در کمپین '{campaign_desc}' {dealer_action_text}.",
        target=campaign
    )
    
    # Notify staff users (using third-person message)
    send_staff_notification(
        sender=user,
        staff_users=staff_users,
        verb=f"{other_verb_text} مجری در کمپین",
        description=f"مجری {user.get_full_name()} در کمپین '{campaign_desc}' {other_action_text}.",
        target=campaign
    )
    send_am_notification(
        sender=user,
        am_users=am_users,
        verb=f"{other_verb_text} مجری در کمپین",
        description=f"مجری {user.get_full_name()} در کمپین '{campaign_desc}' {other_action_text}.",
        target=campaign
    )
    
    # Notify campaign owner if exists (using third-person message)
    if hasattr(campaign, 'customer') and campaign.customer:
        send_notification(
            sender=user,
            recipient=campaign.customer,
            verb=f"{other_verb_text} مجری در کمپین",
            description=f"مجری {user.get_full_name()} در کمپین '{campaign_desc}' {other_action_text}.",
            target=campaign
        )

def notify_campaign_mentor_assignment(campaign, mentor, staff_users, am_users, request_user):
    """
    Send notifications for campaign mentor assignment
    """
    campaign_desc = campaign.get_describe_summrize()
    
    send_notification(
        sender=campaign.customer,
        recipient=mentor,
        verb="انتخاب پیشتیبان",
        description=f"شما به عنوان پیشتیبان برای کمپین '{campaign_desc}' انتخاب شده‌اید.",
        target=campaign
    )   
    
    send_staff_notification(
        sender=campaign.customer,
        staff_users=staff_users,
        verb="انتخاب پیشتیبان",
        description=f"{campaign.assigned_mentor.get_full_name()} به عنوان پیشتیبان برای کمپین '{campaign_desc}' توسط {request_user.get_full_name()}  انتخاب شده‌است.",
        target=campaign
    )
    
    send_am_notification(
        sender=campaign.customer,
        am_users=am_users,
        verb="انتخاب پیشتیبان",
        description=f"{campaign.assigned_mentor.get_full_name()} به عنوان پیشتیبان برای کمپین '{campaign_desc}' توسط {request_user.get_full_name()}  انتخاب شده‌است.",
        target=campaign
    )
    
    send_notification_customer(
        sender=am_users.first(),
        recipient=campaign.customer,
        verb="انتخاب پیشتیبان",
        description=f"پیشتیبان {mentor.get_full_name()} برای کمپین '{campaign_desc}' انتخاب شده‌است.",
        target=campaign
    )

def notify_mentor_request(user, mentor, request_for_mentor, staff_users):
    """
    Send notifications for mentor request actions
    
    Args:
        user: The customer requesting the mentor
        mentor: The mentor being requested
        request_for_mentor: The RequestForMentor object
        staff_users: QuerySet of staff users to notify
    """
    mentor_full_name = mentor.get_full_name()
    
    # Notify the customer (using second person)
    send_notification(
        sender=user,
        recipient=user,
        verb="درخواست منتور",
        description=f"شما درخواست منتور برای {mentor_full_name} را ارسال کرده‌اید. لطفاً منتظر تایید مدیریت باشید.",
        target=request_for_mentor
    )
    
    # Notify staff users (using third person)
    send_staff_notification(
        sender=user,
        staff_users=staff_users,
        verb="درخواست منتور جدید",
        description=f"{user.get_full_name()} درخواست منتور برای {mentor_full_name} ارسال کرده است.",
        target=request_for_mentor
    )

def notify_mentor_request_status(request_for_mentor, status, staff_user, staff_users):
    """
    Send notifications for mentor request status changes
    
    Args:
        request_for_mentor: The RequestForMentor object
        status: Either 'reject' or 'approved'
        staff_user: The staff user who changed the status
        staff_users: QuerySet of staff users to notify
    """
    customer = request_for_mentor.requested_user
    mentor = request_for_mentor.mentor
    mentor_full_name = mentor.get_full_name()
    
    if status == 'reject':
        # Notify the customer about rejection
        send_notification(
            sender=staff_user,
            recipient=customer,
            verb="رد درخواست منتور",
            description=f"درخواست منتور شما برای {mentor_full_name} رد شد.",
            target=request_for_mentor
        )
        
        # Notify staff users
        send_staff_notification(
            sender=staff_user,
            staff_users=staff_users,
            verb="رد درخواست منتور",
            description=f"درخواست منتور {customer.get_full_name()} برای {mentor_full_name} رد شد.",
            target=request_for_mentor
        )
        
    elif status == 'approved':
        # Notify the customer about approval
        send_notification(
            sender=staff_user,
            recipient=customer,
            verb="تایید درخواست منتور",
            description=f"درخواست منتور شما برای {mentor_full_name} تایید شد.",
            target=request_for_mentor
        )
        
        # Notify the mentor about being assigned
        send_notification(
            sender=staff_user,
            recipient=mentor,
            verb="تخصیص کاربر جدید",
            description=f"{customer.get_full_name()} به عنوان کاربر جدید به شما تخصیص داده شد.",
            target=request_for_mentor
        )
        
        # Notify staff users
        send_staff_notification(
            sender=staff_user,
            staff_users=staff_users,
            verb="تایید درخواست منتور",
            description=f"درخواست منتور {customer.get_full_name()} برای {mentor_full_name} تایید شد.",
            target=request_for_mentor
        )

def notify_mentor_activation(staff_user, mentor, staff_users):
    """
    Send notifications for mentor activation
    
    Args:
        staff_user: The staff user who activated the mentor
        mentor: The mentor being activated
        staff_users: QuerySet of staff users to notify
    """
    mentor_full_name = mentor.get_full_name()
    
    # Notify the mentor about activation
    send_notification(
        sender=staff_user,
        recipient=mentor,
        verb="فعال‌سازی حساب منتور",
        description="حساب منتور شما فعال شد. اکنون می‌توانید به پنل خود دسترسی داشته باشید.",
        target=mentor
    )
    
    # Notify staff users
    send_staff_notification(
        sender=staff_user,
        staff_users=staff_users,
        verb="فعال‌سازی حساب منتور",
        description=f"حساب منتور {mentor_full_name} فعال شد.",
        target=mentor
    )

def notify_user_registration(user, staff_users):
    """
    Send notifications for new user registration
    
    Args:
        user: The newly registered user
        staff_users: QuerySet of staff users to notify
    """
    user_full_name = user.get_full_name()
    user_type_persian = {
        'customer': 'مشتری',
        'dealer': 'مجری',
        'mentor': 'منتور'
    }.get(user.user_type, 'کاربر')
    
    # Notify staff users
    send_staff_notification(
        sender=user,
        staff_users=staff_users,
        verb="ثبت‌نام کاربر جدید",
        description=f"{user_full_name} به عنوان {user_type_persian} جدید ثبت‌نام کرده است.",
        target=user
    )

def notify_password_change(user):
    """
    Send notification for password change
    
    Args:
        user: The user who changed their password
    """
    send_notification(
        sender=user,
        recipient=user,
        verb="تغییر رمز عبور",
        description="رمز عبور شما با موفقیت تغییر کرد.",
        target=user
    )

def notify_campaign_winner(campaign, winner, selector, staff_users, am_users):
    """Send notifications when a campaign winner is selected"""
    
    campaign_desc = campaign.topic.name
    
    # Notify winner
    send_notification(
        sender=selector,
        recipient=winner,
        verb="انتخاب برنده کمپین",
        description=f"شما به عنوان برنده کمپین '{campaign_desc}' انتخاب شده‌اید.",
        target=campaign
    )
    
    # Notify campaign owner
    send_notification(
        sender=selector,
        recipient=campaign.customer,
        verb="انتخاب برنده کمپین",
        description=f"{winner.get_full_name()} به عنوان برنده کمپین '{campaign_desc}' انتخاب شد.",
        target=campaign
    )
    
    # Notify staff users
    send_staff_notification(
        sender=selector,
        staff_users=staff_users,
        verb="انتخاب برنده کمپین",
        description=f"{winner.get_full_name()} به عنوان برنده کمپین '{campaign_desc}' انتخاب شد.",
        target=campaign
    )
    
    # Notify AM users
    send_am_notification(
        sender=selector,
        am_users=am_users,
        verb="انتخاب برنده کمپین",
        description=f"{winner.get_full_name()} به عنوان برنده کمپین '{campaign_desc}' انتخاب شد.",
        target=campaign
    )
    
def notify_resume_review(resume, reviewer, old_status, new_status, old_comment=None):
    """
    ارسال اعلان تغییر وضعیت یا تغییر نظر مدیر برای صاحب رزومه
    """
    status_messages = {
        'under_review': 'رزومه شما در حال بررسی قرار گرفت.',
        'needs_editing': 'رزومه شما نیاز به ویرایش دارد.',
        'approved': 'رزومه شما تایید شد.',
        'rejected': 'رزومه شما رد شد.'
    }
    if old_status == new_status and (resume.manager_comment or "") != (old_comment or ""):
        base = "نظر مدیر درباره رزومه شما بروزرسانی شد."
    else:
        base = status_messages.get(new_status, "وضعیت رزومه شما بروزرسانی شد.")
    if resume.manager_comment:
        base += f"\nتوضیح مدیر: {resume.manager_comment}"

    print(f"[notify_resume_review DEBUG] sending notification resume_id={resume.id} old={old_status} new={new_status}")
    notify.send(
        sender=reviewer,
        recipient=resume.user,
        verb="بروزرسانی رزومه",
        description=base,
        target=resume,
        timestamp=timezone.now()
    )
    return True, None

def notify_resume_actions(user, resume, action_type, staff_users, am_users):
    """
    ارسال اعلان برای رزومه (ایجاد یا ویرایش) فقط برای کاربران staff و AM
    action_type: 'create' | 'edit'
    """
    from notifications.signals import notify

    actions = {
        'create': ('ارسال رزومه جدید', f"{user.get_full_name()} رزومه جدید ارسال کرد."),
        'edit': ('ویرایش رزومه', f"{user.get_full_name()} رزومه خود را ویرایش کرد."),
    }
    if action_type not in actions:
        return
    verb, description = actions[action_type]

    for staff in staff_users:
        notify.send(
            sender=user,
            recipient=staff,
            verb=verb,
            description=description,
            target=resume
        )
    for am in am_users:
        notify.send(
            sender=user,
            recipient=am,
            verb=verb,
            description=description,
            target=resume
        )


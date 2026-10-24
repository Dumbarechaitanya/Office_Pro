import json
from datetime import timedelta

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import models
from django.utils import timezone

from base.auth_helpers import get_current_ir_user, login_required_ir
from base.models import ResUsers, ResCompany, IrMailServer
from mail.models import MailMail, MailAttachment


@login_required_ir
def mail_app(request, folder='inbox'):
    current_user = get_current_ir_user(request)
    if not current_user:
        return redirect('login')

    # Get folder counts for badges
    base_user_qs = MailMail.objects.filter(user=current_user)
    folder_counts = {
        'inbox_unread': base_user_qs.filter(folder='inbox', is_read=False).count(),
        'starred_count': base_user_qs.filter(is_starred=True).exclude(folder='trash').count(),
        'sent_count': base_user_qs.filter(folder='sent').count(),
        'drafts_count': base_user_qs.filter(folder='drafts').count(),
        'archive_count': base_user_qs.filter(folder='archive').count(),
        'trash_count': base_user_qs.filter(folder='trash').count(),
        'spam_count': base_user_qs.filter(folder='spam').count(),
    }

    # Label statistics
    labels = [
        {'key': 'work', 'name': 'Work', 'color': '#3b82f6'},
        {'key': 'internal', 'name': 'Internal', 'color': '#10b981'},
        {'key': 'clients', 'name': 'Clients', 'color': '#8b5cf6'},
        {'key': 'finance', 'name': 'Finance', 'color': '#f59e0b'},
        {'key': 'support', 'name': 'Support', 'color': '#ef4444'},
        {'key': 'system', 'name': 'System', 'color': '#64748b'},
        {'key': 'personal', 'name': 'Personal', 'color': '#ec4899'},
    ]
    for lbl in labels:
        lbl['count'] = base_user_qs.filter(label=lbl['key']).exclude(folder='trash').count()

    users = ResUsers.objects.filter(is_active=True).order_by('username')
    mail_servers = IrMailServer.objects.filter(is_active=True).order_by('sequence', 'name')
    companies = ResCompany.objects.all().order_by('name')[:15]

    return render(request, 'mail/mail_app.html', {
        'current_user': current_user,
        'current_folder': folder or 'inbox',
        'folder_counts': folder_counts,
        'labels': labels,
        'users': users,
        'mail_servers': mail_servers,
        'companies': companies,
    })


@login_required_ir
def mail_api_emails(request):
    current_user = get_current_ir_user(request)
    if not current_user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    folder = request.GET.get('folder', 'inbox').strip().lower()
    label = request.GET.get('label', '').strip().lower()
    q = request.GET.get('q', '').strip()
    filter_type = request.GET.get('filter', '').strip().lower()
    try:
        page = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page = 1
    try:
        page_size = int(request.GET.get('page_size', 30))
    except (ValueError, TypeError):
        page_size = 30

    qs = MailMail.objects.filter(user=current_user)

    if folder == 'starred':
        qs = qs.filter(is_starred=True).exclude(folder='trash')
    elif folder in ['inbox', 'sent', 'drafts', 'archive', 'trash', 'spam']:
        qs = qs.filter(folder=folder)
    
    if label:
        qs = qs.filter(label=label)

    if filter_type == 'unread':
        qs = qs.filter(is_read=False)
    elif filter_type == 'starred':
        qs = qs.filter(is_starred=True)
    elif filter_type == 'attachment':
        qs = qs.filter(attachments__isnull=False).distinct()

    if q:
        from django.db.models import Q
        qs = qs.filter(
            Q(subject__icontains=q) |
            Q(body_text__icontains=q) |
            Q(email_from__icontains=q) |
            Q(email_to__icontains=q) |
            Q(res_name__icontains=q)
        )

    total_count = len(qs) if isinstance(qs, list) else qs.count()

    if hasattr(qs, 'order_by'):
        qs = qs.order_by('-date', '-created_at')

    start = (page - 1) * page_size
    end = start + page_size
    page_emails = qs[start:end]

    emails_data = []
    for m in page_emails:
        emails_data.append({
            'id': m.id,
            'subject': m.subject or '(No Subject)',
            'snippet': m.snippet,
            'email_from': m.email_from,
            'sender_name': m.sender_name,
            'sender_email': m.sender_email,
            'avatar_initial': m.avatar_initial,
            'avatar_color': m.avatar_color,
            'email_to': m.email_to,
            'folder': m.folder,
            'label': m.label,
            'is_read': m.is_read,
            'is_starred': m.is_starred,
            'is_important': m.is_important,
            'date_formatted': m.formatted_date,
            'date_full': m.formatted_full_date,
            'has_attachments': m.has_attachments,
            'res_model': m.res_model,
            'res_id': m.res_id,
            'res_name': m.res_name,
            'record_url': m.record_url,
        })

    base_user_qs = MailMail.objects.filter(user=current_user)
    folder_counts = {
        'inbox_unread': base_user_qs.filter(folder='inbox', is_read=False).count() if hasattr(base_user_qs, 'count') else 0,
        'starred_count': base_user_qs.filter(is_starred=True).exclude(folder='trash').count() if hasattr(base_user_qs, 'count') else 0,
        'sent_count': base_user_qs.filter(folder='sent').count() if hasattr(base_user_qs, 'count') else 0,
        'drafts_count': base_user_qs.filter(folder='drafts').count() if hasattr(base_user_qs, 'count') else 0,
        'archive_count': base_user_qs.filter(folder='archive').count() if hasattr(base_user_qs, 'count') else 0,
        'trash_count': base_user_qs.filter(folder='trash').count() if hasattr(base_user_qs, 'count') else 0,
    }

    return JsonResponse({
        'success': True,
        'emails': emails_data,
        'total_count': total_count,
        'page': page,
        'page_size': page_size,
        'folder_counts': folder_counts,
    })


@login_required_ir
def mail_api_email_detail(request, email_id):
    current_user = get_current_ir_user(request)
    if not current_user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        email = MailMail.objects.prefetch_related('attachments').get(id=email_id, user=current_user)
    except MailMail.DoesNotExist:
        return JsonResponse({'error': 'Email not found'}, status=404)

    if not email.is_read:
        email.is_read = True
        email.save(update_fields=['is_read'])

    attachments_data = []
    for att in email.attachments.all():
        attachments_data.append({
            'id': att.id,
            'name': att.name,
            'size': att.formatted_size,
            'icon': att.file_icon,
            'url': att.file.url if att.file else '#',
        })

    from django.db.models import Q
    if email.parent_mail:
        thread_qs = MailMail.objects.filter(
            Q(id=email.parent_mail_id) | Q(parent_mail_id=email.parent_mail_id),
            user=current_user
        ).order_by('date')
    else:
        thread_qs = MailMail.objects.filter(
            Q(id=email.id) | Q(parent_mail_id=email.id),
            user=current_user
        ).order_by('date')

    thread_data = []
    for t in thread_qs:
        t_attachments = [{'id': a.id, 'name': a.name, 'size': a.formatted_size, 'icon': a.file_icon, 'url': a.file.url if a.file else '#'} for a in t.attachments.all()]
        thread_data.append({
            'id': t.id,
            'subject': t.subject,
            'body_html': t.body_html or f"<p>{t.body_text}</p>",
            'body_text': t.body_text,
            'email_from': t.email_from,
            'sender_name': t.sender_name,
            'sender_email': t.sender_email,
            'avatar_initial': t.avatar_initial,
            'avatar_color': t.avatar_color,
            'email_to': t.email_to,
            'date_formatted': t.formatted_date,
            'date_full': t.formatted_full_date,
            'attachments': t_attachments,
        })

    email_dict = {
        'id': email.id,
        'subject': email.subject,
        'body_html': email.body_html or f"<p>{email.body_text}</p>",
        'body_text': email.body_text,
        'email_from': email.email_from,
        'sender_name': email.sender_name,
        'sender_email': email.sender_email,
        'avatar_initial': email.avatar_initial,
        'avatar_color': email.avatar_color,
        'email_to': email.email_to,
        'email_cc': email.email_cc or '',
        'email_bcc': email.email_bcc or '',
        'reply_to': email.reply_to or '',
        'folder': email.folder,
        'label': email.label,
        'is_read': email.is_read,
        'is_starred': email.is_starred,
        'is_important': email.is_important,
        'date_formatted': email.formatted_date,
        'date_full': email.formatted_full_date,
        'attachments': attachments_data,
        'res_model': email.res_model,
        'res_id': email.res_id,
        'res_name': email.res_name,
        'record_url': email.record_url,
        'thread': thread_data,
    }

    return JsonResponse({
        'success': True,
        'email': email_dict,
        **email_dict,
    })


@login_required_ir
def mail_api_compose(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    current_user = get_current_ir_user(request)
    if not current_user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    email_to = data.get('email_to', '').strip()
    email_cc = data.get('email_cc', '').strip()
    email_bcc = data.get('email_bcc', '').strip()
    subject = data.get('subject', '').strip() or '(No Subject)'
    body_html = data.get('body_html', '').strip()
    body_text = data.get('body_text', '').strip()
    is_draft = data.get('is_draft', False) in (True, 'true', '1', 1)
    label = data.get('label', 'work').strip()
    res_model = data.get('res_model', '').strip() or None
    res_id = int(data.get('res_id', 0) or 0)
    res_name = data.get('res_name', '').strip() or None
    mail_server_id = data.get('mail_server_id')
    attachment_ids = data.get('attachment_ids', [])

    if not email_to and not is_draft:
        return JsonResponse({'error': 'Recipient email (To) is required.'}, status=400)

    sender_display = f"{current_user.username} <{current_user.email or current_user.username + '@officepro.io'}>"
    folder = 'drafts' if is_draft else 'sent'
    state = 'draft' if is_draft else 'sent'

    mail_server = None
    if mail_server_id:
        mail_server = IrMailServer.objects.filter(id=mail_server_id, is_active=True).first()

    sent_mail = MailMail.objects.create(
        user=current_user,
        sender_user=current_user,
        email_from=sender_display,
        email_to=email_to,
        email_cc=email_cc,
        email_bcc=email_bcc,
        subject=subject,
        body_html=body_html or f"<p>{body_text}</p>",
        body_text=body_text or "",
        folder=folder,
        state=state,
        is_read=True,
        is_starred=False,
        label=label,
        res_model=res_model,
        res_id=res_id,
        res_name=res_name,
        mail_server=mail_server,
        date=timezone.now()
    )

    if attachment_ids:
        att_objs = MailAttachment.objects.filter(id__in=attachment_ids)
        sent_mail.attachments.set(att_objs)

    if not is_draft:
        from django.db.models import Q
        recipient_emails = [e.strip().lower() for e in email_to.replace(';', ',').split(',') if e.strip()]
        for rec_email in recipient_emails:
            clean_rec = rec_email.split('<')[-1].replace('>', '').strip()
            internal_user = ResUsers.objects.filter(
                Q(email__iexact=clean_rec) | Q(username__iexact=clean_rec.split('@')[0]),
                is_active=True
            ).first()
            if internal_user and internal_user.id != current_user.id:
                inbox_mail = MailMail.objects.create(
                    user=internal_user,
                    sender_user=current_user,
                    recipient_user=internal_user,
                    email_from=sender_display,
                    email_to=email_to,
                    email_cc=email_cc,
                    subject=subject,
                    body_html=body_html or f"<p>{body_text}</p>",
                    body_text=body_text or "",
                    folder='inbox',
                    state='received',
                    is_read=False,
                    label=label,
                    res_model=res_model,
                    res_id=res_id,
                    res_name=res_name,
                    date=timezone.now()
                )
                if attachment_ids:
                    inbox_mail.attachments.set(att_objs)

    return JsonResponse({
        'success': True,
        'email_id': sent_mail.id,
        'message': 'Draft saved' if is_draft else 'Email sent successfully'
    })


@login_required_ir
def mail_api_reply(request, email_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    current_user = get_current_ir_user(request)
    if not current_user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        parent_mail = MailMail.objects.get(id=email_id, user=current_user)
    except MailMail.DoesNotExist:
        return JsonResponse({'error': 'Original email not found'}, status=404)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    body_html = data.get('body_html', '').strip()
    body_text = data.get('body_text', '').strip()
    reply_all = data.get('reply_all', False) in (True, 'true', '1', 1)
    attachment_ids = data.get('attachment_ids', [])

    if not body_html and not body_text:
        return JsonResponse({'error': 'Message body cannot be empty.'}, status=400)

    if parent_mail.folder == 'sent':
        email_to = parent_mail.email_to
    else:
        email_to = parent_mail.email_from

    email_cc = parent_mail.email_cc if reply_all else ''
    sender_display = f"{current_user.username} <{current_user.email or current_user.username + '@officepro.io'}>"
    subject = parent_mail.subject if parent_mail.subject.startswith('Re: ') else f"Re: {parent_mail.subject}"

    reply_mail = MailMail.objects.create(
        user=current_user,
        sender_user=current_user,
        email_from=sender_display,
        email_to=email_to,
        email_cc=email_cc,
        subject=subject,
        body_html=body_html or f"<p>{body_text}</p>",
        body_text=body_text,
        folder='sent',
        state='sent',
        is_read=True,
        label=parent_mail.label,
        res_model=parent_mail.res_model,
        res_id=parent_mail.res_id,
        res_name=parent_mail.res_name,
        parent_mail=parent_mail.parent_mail or parent_mail,
        date=timezone.now()
    )

    if attachment_ids:
        att_objs = MailAttachment.objects.filter(id__in=attachment_ids)
        reply_mail.attachments.set(att_objs)

    return JsonResponse({
        'success': True,
        'email_id': reply_mail.id,
        'message': 'Reply sent successfully'
    })


@login_required_ir
def mail_api_star_toggle(request, email_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    current_user = get_current_ir_user(request)
    if not current_user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        email = MailMail.objects.get(id=email_id, user=current_user)
    except MailMail.DoesNotExist:
        return JsonResponse({'error': 'Email not found'}, status=404)

    email.is_starred = not email.is_starred
    email.save(update_fields=['is_starred'])

    return JsonResponse({'success': True, 'is_starred': email.is_starred})


@login_required_ir
def mail_api_batch_action(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    current_user = get_current_ir_user(request)
    if not current_user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    action = data.get('action', '').strip()
    email_ids = data.get('email_ids', [])
    label = str(data.get('label') or data.get('value') or '').strip()

    if not email_ids:
        return JsonResponse({'error': 'No emails selected'}, status=400)

    qs = MailMail.objects.filter(id__in=email_ids, user=current_user)
    count = qs.count()

    if action == 'mark_read':
        qs.update(is_read=True)
    elif action == 'mark_unread':
        qs.update(is_read=False)
    elif action == 'star':
        qs.update(is_starred=True)
    elif action == 'unstar':
        qs.update(is_starred=False)
    elif action == 'archive':
        qs.update(folder='archive')
    elif action == 'trash':
        qs.update(folder='trash')
    elif action == 'restore':
        qs.update(folder='inbox')
    elif action == 'delete_permanently':
        qs.delete()
    elif action == 'set_label' and label:
        qs.update(label=label)
    else:
        return JsonResponse({'error': f'Invalid action: {action}'}, status=400)

    return JsonResponse({'success': True, 'affected_count': count})


@login_required_ir
def mail_api_attachment_upload(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    current_user = get_current_ir_user(request)
    if not current_user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    uploaded_file = request.FILES['file']
    attachment = MailAttachment.objects.create(
        name=uploaded_file.name,
        file=uploaded_file,
        file_size=uploaded_file.size,
        content_type=uploaded_file.content_type
    )

    return JsonResponse({
        'id': attachment.id,
        'name': attachment.name,
        'size': attachment.formatted_size,
        'icon': attachment.file_icon,
        'url': attachment.file.url if attachment.file else '#'
    })

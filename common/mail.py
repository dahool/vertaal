from django.core import mail

def send_mass_mail_em(email_message_list, fail_silently=False):
    connection = mail.get_connection(fail_silently=fail_silently) 
    r =  connection.send_messages(email_message_list)
    return r
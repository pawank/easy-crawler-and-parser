#!/usr/bin/env python
import os
import sys
import smtplib
import traceback



def send_mail(fromaddr,toaddrs,msg,body):
    try:
            gmail_user = os.environ["APP_EMAIL_USER"]
            gmail_pwd = os.environ["APP_EMAIL_PWD"]
            email_host = os.environ["APP_EMAIL_HOST"]
            FROM = fromaddr
            TO = toaddrs #must be a list
            SUBJECT = msg
            TEXT = body

            # Prepare actual message
            message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
            try:
                #server = smtplib.SMTP(SERVER) 
                server = smtplib.SMTP(email_host, 587) #or port 465 doesn't seem to work!
                #server = smtplib.SMTP_SSL("smtp.gmail.com", 587)
                server.ehlo()
                server.starttls()
                server.login(gmail_user, gmail_pwd)
                server.sendmail(FROM, TO, message)
                #server.quit()
                server.close()
                print('Successfully sent the mail to users - %s' % str(toaddrs))
            except:
                print("Failed to send mail with subject - %s" % msg)
                print(traceback.format_exc())
        # Credentials (if needed)
    except:
        print("Failed to send mail with subject - %s" % msg)
        print(traceback.format_exc())

if __name__ == "__main__":
        args = sys.argv
        print(args)
        #send_mail("care@acelrtech.com",args[1].split(";"),args[2],args[3])
        send_mail("admin@rapidor.co",args[1].split(";"),args[2],args[3])
        #send_mail("admin@rapidor.co","pawan@acelrtech.com;pawan.kumar@acelrtech.com".split(";"),"Testing","Test body")

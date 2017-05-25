import os
import errno
import subprocess
import shlex
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from cbio.core import DirectoryExists

def make_dirs(path, mode=0755):
    """
    Recursive directory creation function.
    """
    try:
        os.makedirs(path, mode)
    except OSError as e:
        if e.errno == errno.EEXIST:
            raise DirectoryExists("directory already exists: {}".format(path), path)
        raise


def load_md5sum_from_file(path):
    """
    Extract the md5sum from file.
    """
    md5sum_path = "{}.md5sum".format(path)
    with open(md5sum_path, 'rU') as md5sum_file:
        return md5sum_file.read().split()[0]


def run(cmd, cwd=None, shell=False):
    """
    Run command on local host.

    :param cmd (string) - the command to run, mandatory
    :param cwd (string) - the directory under which to run the command
    :param shell (bool) - allow shell features (try to avoid if possible), optional
    :returns: (exit_code, stdout, stderr)
    
    """
    p = subprocess.Popen(shlex.split(cmd), cwd=cwd, shell=shell, 
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    exit_code = p.poll()

    return exit_code, stdout, stderr

def send_mail(send_from, send_to, subject, text, mail_host, files=None):
    assert isinstance(send_to, list)

    msg = MIMEMultipart(
        From=send_from,
        To=COMMASPACE.join(send_to),
        Date=formatdate(localtime=True),
        Subject=subject
    )
    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            msg.attach(MIMEApplication(
                fil.read(),
                Content_Disposition='attachment; filename="%s"' % basename(f),
                Name=basename(f)
            ))

    smtp = smtplib.SMTP(mail_host)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()



def send_email(mail_host, send_from, send_to, subject, body):
    smtpserver = smtplib.SMTP(mail_host, 25)

    message = "Subject: {0}\n\n{1}".format(subject, body)

    smtpserver.sendmail(send_from, send_to, message)
    smtpserver.quit()


def send_html_email(mail_host, send_from, send_to, subject, html_body):
    msg = MIMEMultipart('alternative')
    msg["To"] = COMMASPACE.join(send_to)
    msg["From"] = send_from
    msg["Subject"] = subject

    part = MIMEText(html_body, "html")
    msg.attach(part)

    s = smtplib.SMTP(mail_host)
    s.sendmail(send_from, send_to, msg.as_string())
    s.close()
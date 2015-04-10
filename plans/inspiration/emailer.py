import smtplib
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.mime.base import MIMEBase

ctype, encoding = mimetypes.guess_type("./inspirations.pdf")
if ctype is None or encoding is not None:
    # No guess could be made, or the file is encoded (compressed), so
    # use a generic bag-of-bits type.
    ctype = 'application/octet-stream'
maintype, subtype = ctype.split('/', 1)
msg = MIMEBase(maintype, subtype)
msg.set_payload(file("./inspirations.pdf").read())


mailer = smtplib.SMTP()
mailer.connect()
mailer.sendmail("ken.mc@atlas", ["ken.mccullagh@s3group.com"], msg.as_string())
mailer.close()

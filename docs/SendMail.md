# class SendMail - email library

Usage:
```python
from ezblock import *

sendmail = SendMail(mail_host, sender, mail_pass)                     # create an SendMail object 
sendmail.send(receivers, msg, subject)                    # send a e-Mail
```
## Constructors
```class ezblock.SendMail(pin)```
Create an SendMail object associated with the given pin. This allows you to then read analog values on that pin.

## Methods
- send -You can send mail by thie function.
```python
SendMail.send(receivers, msg, subject)
```
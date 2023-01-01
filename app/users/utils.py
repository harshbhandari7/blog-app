import secrets
import os

from PIL import Image
from flask_mail import Message
from flask import url_for, current_app
from app import mail

# func to create img file and save
def save_picture(form_picture, username):
    # random hex to create filename, but I have replaced it with username
    random_hex = secrets.token_hex(8)
    file_name, file_ext = os.path.splitext(form_picture.filename)
    picture_filename = f"{username}{file_ext}"
    
    picture_path = os.path.join(current_app.root_path, 'static/images/profile_imgs', picture_filename)
    
    # resizing img to save space on filesystem
    output_size = (150, 150)
    img = Image.open(form_picture)
    img.thumbnail(output_size)

    img.save(picture_path)

    return picture_filename

def send_password_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
        sender='harshbhandari32@gmail.com',
        recipients=[user.email])
    
    msg.body = f'''
        To reset your password, visit the following link:
{url_for('users.reset_password_token', token=token, _external=True)} 

If this is not requested by you then Please ignore the mail and no change will be made.
'''
    # sending msg thru created mail instance
    mail.send(msg)
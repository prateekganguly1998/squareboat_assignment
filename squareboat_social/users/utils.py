import secrets
import os
from PIL import Image
from flask_mail import Message
from flask import url_for, current_app
from squareboat_social import mail

def save_picture(form_picture, type):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = str()
    if type == 'profile':
        picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
        output_size = (125,125)
        i = Image.open(form_picture) 
        i.thumbnail(output_size)
        i.save(picture_path)
    else:
        picture_path = os.path.join(current_app.root_path, 'static/post_pictures', picture_fn)
        form_picture.save(picture_path)

    return picture_fn


# Reset password Logic

def send_reset_email(user):
    token = user.get_token()
    message = Message('Did you request a password reset??',
     sender='noreply@sbassignment.com',
    recipients=[user.email])
    message.body = f'''To reset your password visit the following link:
    {url_for('users.reset_password', token = token, _external = True)}


    Please ignore if you did not make this request   
    
    '''
    mail.send(message)

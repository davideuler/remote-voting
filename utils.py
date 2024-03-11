import qrcode
import io
from flask import send_file
from base64 import b64encode

#        qr.add_data(url_for('vote.vote', vote_session_id=vote_session.id, _external=True))
#        img.save(buffered)

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    qr_code = b64encode(img_io.getvalue()).decode('utf-8')
    return qr_code

def summarize_votes(votes, vote_type):
    # This function should summarize the votes based on the vote_type
    # For now, it's a placeholder that returns an empty summary
    return {}

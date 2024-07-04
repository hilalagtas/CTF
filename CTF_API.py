from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()  # .env dosyasını yükler

app = Flask(__name__)
app.config['SECRET_KEY'] = "'aynenaskosecretfalan"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/database_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    soyad = db.Column(db.String(100), nullable=False)
    telefon = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    sifre = db.Column(db.String(200), nullable=False)

    def __init__(self, ad, soyad, telefon, email, sifre):
        self.ad = ad
        self.soyad = soyad
        self.telefon = telefon
        self.email = email
        self.sifre = generate_password_hash(sifre)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_text = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    def __init__(self, sender_id, receiver_id, message_text):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message_text = message_text


def get_conversations(user_id):
    sent_messages = db.session.query(Message.receiver_id).filter(Message.sender_id == user_id).distinct()
    received_messages = db.session.query(Message.sender_id).filter(Message.receiver_id == user_id).distinct()
    conversations = sent_messages.union(received_messages).all()
    user_ids = [user_id for (user_id,) in conversations]
    users = User.query.filter(User.id.in_(user_ids)).all()
    return users


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/kayit', methods=['POST'])
def kayit():
    ad = request.form['ad']
    soyad = request.form['soyad']
    telefon = request.form['telefon']
    email = request.form['email']
    sifre = request.form['sifre']

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Bu e-posta adresi zaten kullanılıyor.')
        return redirect(url_for('index'))

    new_user = User(ad, soyad, telefon, email, sifre)
    db.session.add(new_user)
    db.session.commit()

    return 'Kayıt Başarılı!'


@app.route('/giris', methods=['POST'])
def giris():
    email = request.form['giris_email']
    sifre = request.form['giris_sifre']

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.sifre, sifre):
        return redirect(url_for('mesajlar', user_id=user.id))

    return 'Giriş Başarısız!'


@app.route('/mesajlar', methods=['GET', 'POST'])
@app.route('/mesajlar', methods=['GET', 'POST'])
def mesajlar():
    user_id = request.args.get('user_id', type=int)
    receiver_id = request.args.get('receiver_id', type=int)
    receiver_email = request.args.get('receiver_email', type=str)

    if request.method == 'POST':
        data = request.get_json()
        sender_id = data['sender_id']
        receiver_email = data['receiver_email']
        message_text = data['message_text']

        receiver = User.query.filter_by(email=receiver_email).first()
        if not receiver:
            return jsonify({'success': False, 'error': 'Alıcı bulunamadı!'})

        new_message = Message(sender_id, receiver.id, message_text)
        db.session.add(new_message)
        db.session.commit()
        return jsonify({'success': True})

    if receiver_email and not receiver_id:
        receiver = User.query.filter_by(email=receiver_email).first()
        if receiver:
            receiver_id = receiver.id
        else:
            flash('Alıcı bulunamadı!')
            return redirect(url_for('mesajlar', user_id=user_id))

    conversations = get_conversations(user_id)
    if receiver_id:
        received_messages = Message.query.filter_by(receiver_id=user_id, sender_id=receiver_id).all()
        sent_messages = Message.query.filter_by(sender_id=user_id, receiver_id=receiver_id).all()
        all_messages = received_messages + sent_messages
        all_messages.sort(key=lambda x: x.timestamp)
    else:
        all_messages = []

    user = User.query.get(user_id)

    return render_template(
        'mesajlar.html',
        all_messages=all_messages,
        conversations=conversations,
        user_id=user_id,
        receiver_id=receiver_id,
        receiver_email=receiver_email,
        user_ad=user.ad,
        user_soyad=user.soyad,
        user_email=user.email
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Veritabanı tablolarını oluşturur
    app.run(debug=True)

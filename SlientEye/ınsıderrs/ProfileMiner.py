import instaloader
import time
import json
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

def get_profile_data(L, username):
    profile = instaloader.Profile.from_username(L.context, username)
    return {
        "followers": profile.followers,
        "posts": profile.mediacount
    }

def send_email(sender_email, sender_password, receiver_email, subject, body):
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)
    print("📧 Mail gönderildi.")

def load_previous_data(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        return {}

def save_current_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)

def monitor(username, sender_email, sender_password, receiver_email, instagram_email, instagram_password, interval=60):
    data_file = f"{username}_data.json"
    L = instaloader.Instaloader()
    
    L.context._session.headers.update({
        "User-Agent": "Instagram 123.0.0.21.114 Android (28/9; 420dpi; 1080x1920; samsung; SM-G960F; starlte; samsungexynos9810; en_US)"
    })
    
    try:
        L.login(instagram_email, instagram_password)
        print("Instagram'a başarıyla giriş yapıldı.")
    except Exception as e:
        print(f"Instagram login hatası: {e}")
        return

    while True:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Kontrol ediliyor...")
        try:
            current_data = get_profile_data(L, username)
            previous_data = load_previous_data(data_file)
            changes = []

            if not previous_data:
                changes.append("İlk veri kaydı yapıldı.")
            else:
                # Takipçi sayısı değiştiyse (artış veya azalış)
                diff_followers = current_data["followers"] - previous_data.get("followers", 0)
                if diff_followers > 0:
                    changes.append(f"{diff_followers} yeni takipçi eklendi.")
                elif diff_followers < 0:
                    changes.append(f"{abs(diff_followers)} takipçi kaybedildi.")

                # Gönderi sayısı değiştiyse (artış veya azalış - normalde azalış olmaz ama kontrol edelim)
                diff_posts = current_data["posts"] - previous_data.get("posts", 0)
                if diff_posts > 0:
                    changes.append(f"{diff_posts} yeni gönderi paylaşıldı.")
                elif diff_posts < 0:
                    changes.append(f"{abs(diff_posts)} gönderi silindi.")

            if changes:
                print("🔔 Değişiklik tespit edildi!")
                for c in changes:
                    print(" -", c)
                body = f"{username} hesabında değişiklikler:\n\n" + "\n".join(changes)
                subject = f"{username} Instagram Güncelleme"
                send_email(sender_email, sender_password, receiver_email, subject, body)
                save_current_data(data_file, current_data)
            else:
                print("✅ Değişiklik yok.")

        except Exception as e:
            print(f"❌ Hata oluştu: {e}")

        print(f"⏳ {interval} saniye bekleniyor...\n")
        time.sleep(interval)

if __name__ == "__main__":
    username = "Hedef instagram hesabı"
    sender_email = "gönderici mail"
    sender_password = "gönderici mail şifresi ama uygulama şifresi"
    receiver_email = "Alıcı mail"
    instagram_email = "gözlem yapcak hesabın"
    instagram_password = "hesabın şifresi"

    monitor(username, sender_email, sender_password, receiver_email, instagram_email, instagram_password, interval=60)

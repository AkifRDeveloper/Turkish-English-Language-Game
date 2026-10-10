from flask import Flask, render_template, request, jsonify, session
import random
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "kelime-oyunu-super-secret-change-me"
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "kelime_oyunu.db"

# Büyük kelime havuzu: (Türkçe, İngilizce, kategori, örnek cümle)
WORDS = {
    "kolay": [
        ("elma", "apple", "Yiyecek", "I eat an apple."), ("ev", "house", "Yer", "My house is small."),
        ("araba", "car", "Ulaşım", "The car is fast."), ("kitap", "book", "Okul", "This book is interesting."),
        ("su", "water", "Yiyecek", "I drink water."), ("köpek", "dog", "Hayvan", "The dog is friendly."),
        ("kedi", "cat", "Hayvan", "The cat is sleeping."), ("okul", "school", "Okul", "I go to school."),
        ("masa", "table", "Ev", "The book is on the table."), ("kalem", "pencil", "Okul", "I need a pencil."),
        ("güneş", "sun", "Doğa", "The sun is bright."), ("ay", "moon", "Doğa", "The moon is beautiful."),
        ("ağaç", "tree", "Doğa", "The tree is tall."), ("süt", "milk", "Yiyecek", "I drink milk."),
        ("ekmek", "bread", "Yiyecek", "The bread is fresh."), ("kapı", "door", "Ev", "Open the door."),
        ("pencere", "window", "Ev", "Close the window."), ("arkadaş", "friend", "İnsan", "My friend is funny."),
        ("anne", "mother", "Aile", "My mother is kind."), ("baba", "father", "Aile", "My father is tall."),
        ("kuş", "bird", "Hayvan", "The bird can fly."), ("balık", "fish", "Hayvan", "The fish is blue."),
        ("muz", "banana", "Yiyecek", "I like bananas."), ("sandalye", "chair", "Ev", "Sit on the chair."),
        ("çanta", "bag", "Eşya", "My bag is heavy."), ("ayakkabı", "shoe", "Eşya", "My shoe is new."),
        ("yağmur", "rain", "Doğa", "I like the rain."), ("kar", "snow", "Doğa", "The snow is white."),
        ("kırmızı", "red", "Renk", "The car is red."), ("mavi", "blue", "Renk", "The sky is blue."),
        ("mutlu", "happy", "Duygu", "I am happy."), ("büyük", "big", "Sıfat", "The house is big."),
        ("küçük", "small", "Sıfat", "The box is small."), ("sıcak", "hot", "Sıfat", "The tea is hot."),
        ("soğuk", "cold", "Sıfat", "The water is cold."), ("koşmak", "run", "Fiil", "I run every morning."),
        ("oynamak", "play", "Fiil", "We play together."), ("gülmek", "laugh", "Fiil", "They laugh a lot."),
    ],
    "orta": [
        ("üzgün", "sad", "Duygu", "He looks sad."), ("güzel", "beautiful", "Sıfat", "The view is beautiful."),
        ("hızlı", "fast", "Sıfat", "This train is fast."), ("yavaş", "slow", "Sıfat", "The turtle is slow."),
        ("şehir", "city", "Yer", "The city is crowded."), ("ülke", "country", "Yer", "Turkey is a country."),
        ("yemek", "food", "Yiyecek", "The food is delicious."), ("öğretmen", "teacher", "Okul", "My teacher is helpful."),
        ("öğrenci", "student", "Okul", "She is a good student."), ("hastane", "hospital", "Yer", "The hospital is nearby."),
        ("kütüphane", "library", "Yer", "I study in the library."), ("bilgisayar", "computer", "Teknoloji", "My computer is fast."),
        ("telefon", "phone", "Teknoloji", "My phone is new."), ("tatil", "holiday", "Seyahat", "We are on holiday."),
        ("havaalanı", "airport", "Seyahat", "The airport is busy."), ("sabah", "morning", "Zaman", "Good morning!"),
        ("akşam", "evening", "Zaman", "Good evening!"), ("gelecek", "future", "Zaman", "Think about the future."),
        ("başlamak", "start", "Fiil", "Let's start now."), ("bitirmek", "finish", "Fiil", "I finish my homework."),
        ("öğrenmek", "learn", "Fiil", "I learn English."), ("unutmak", "forget", "Fiil", "Don't forget this."),
        ("seyahat", "travel", "Seyahat", "I love to travel."), ("macera", "adventure", "Hobi", "It was a great adventure."),
        ("hikaye", "story", "Okul", "Tell me a story."), ("soru", "question", "Okul", "I have a question."),
        ("cevap", "answer", "Okul", "I know the answer."), ("güvenli", "safe", "Sıfat", "This place is safe."),
        ("tehlikeli", "dangerous", "Sıfat", "That road is dangerous."), ("gürültülü", "noisy", "Sıfat", "The street is noisy."),
        ("sessiz", "quiet", "Sıfat", "The room is quiet."), ("kalabalık", "crowded", "Sıfat", "The bus is crowded."),
        ("önemli", "important", "Sıfat", "This is important."), ("farklı", "different", "Sıfat", "Everyone is different."),
        ("seçmek", "choose", "Fiil", "Choose one answer."), ("yardım etmek", "help", "Fiil", "Can you help me?"),
        ("denemek", "try", "Fiil", "Try again."), ("hatırlamak", "remember", "Fiil", "Remember this word."),
    ],
    "zor": [
        ("teknoloji", "technology", "Teknoloji", "Technology changes quickly."), ("üniversite", "university", "Eğitim", "She studies at university."),
        ("başarı", "success", "Kariyer", "Success takes time."), ("sorumluluk", "responsibility", "Yaşam", "It is a big responsibility."),
        ("çevre", "environment", "Doğa", "We should protect the environment."), ("geliştirmek", "develop", "Fiil", "We develop new ideas."),
        ("deneyim", "experience", "Yaşam", "Experience is valuable."), ("fırsat", "opportunity", "Yaşam", "This is a great opportunity."),
        ("bağımsız", "independent", "Sıfat", "She is independent."), ("yaratıcılık", "creativity", "Yetenek", "Creativity is important."),
        ("iletişim", "communication", "Yaşam", "Good communication helps."), ("bilgi", "information", "Okul", "I need more information."),
        ("hayal gücü", "imagination", "Yetenek", "Use your imagination."), ("telaffuz", "pronunciation", "Dil", "Pronunciation takes practice."),
        ("mükemmel", "excellent", "Sıfat", "You did an excellent job."), ("araştırma", "research", "Okul", "The research is useful."),
        ("gelecek nesil", "next generation", "Toplum", "The next generation will learn."), ("problem çözme", "problem solving", "Yetenek", "Problem solving is useful."),
        ("karar vermek", "decide", "Fiil", "You must decide today."), ("başarmak", "achieve", "Fiil", "You can achieve your goal."),
        ("merak", "curiosity", "Yetenek", "Curiosity helps us learn."), ("sabır", "patience", "Yetenek", "Patience is important."),
        ("kararlılık", "determination", "Yetenek", "Determination leads to progress."), ("olağanüstü", "extraordinary", "Sıfat", "It was an extraordinary day."),
        ("sürdürülebilir", "sustainable", "Doğa", "We need sustainable solutions."), ("keşfetmek", "discover", "Fiil", "Let's discover something new."),
        ("başlangıç", "beginning", "Zaman", "Every journey has a beginning."), ("başarıya ulaşmak", "succeed", "Fiil", "Work hard to succeed."),
        ("etkili", "effective", "Sıfat", "This method is effective."), ("karmaşık", "complex", "Sıfat", "It is a complex problem."),
        ("güvenilir", "reliable", "Sıfat", "He is reliable."), ("olağan", "ordinary", "Sıfat", "It was an ordinary day."),
        ("beklenti", "expectation", "Yaşam", "My expectation was different."), ("ilerleme", "progress", "Yaşam", "You are making progress."),
        ("çözüm", "solution", "Okul", "We found a solution."), ("kanıt", "evidence", "Okul", "We need evidence."),
        ("davranış", "behavior", "Yaşam", "His behavior was strange."), ("başlangıç noktası", "starting point", "Yaşam", "This is a good starting point."),
    ]
}


def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with get_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            best_score INTEGER NOT NULL DEFAULT 0,
            best_streak INTEGER NOT NULL DEFAULT 0,
            xp INTEGER NOT NULL DEFAULT 0,
            games INTEGER NOT NULL DEFAULT 0,
            correct INTEGER NOT NULL DEFAULT 0
        )""")
        # Eski DB'ler için eksik sütunları ekle.
        columns = {r[1] for r in db.execute("PRAGMA table_info(users)").fetchall()}
        for name, definition in [("xp", "INTEGER NOT NULL DEFAULT 0"), ("games", "INTEGER NOT NULL DEFAULT 0"), ("correct", "INTEGER NOT NULL DEFAULT 0")]:
            if name not in columns:
                db.execute(f"ALTER TABLE users ADD COLUMN {name} {definition}")
        db.commit()

init_db()


def level_from_xp(xp):
    return max(1, xp // 250 + 1)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/kelime", methods=["POST"])
def word():
    data = request.get_json(silent=True) or {}
    difficulty = data.get("zorluk", "kolay")
    used = set(data.get("used", []))
    if difficulty not in WORDS:
        return jsonify({"error": "Geçersiz zorluk."}), 400
    pool = [w for w in WORDS[difficulty] if w[1] not in used] or WORDS[difficulty]
    tr, en, category, example = random.choice(pool)
    return jsonify({"turkce": tr, "ingilizce": en, "kategori": category, "ornek": example})


@app.route("/auth/status")
def auth_status():
    username = session.get("username")
    if not username:
        return jsonify({"logged_in": False, "username": None, "best_score": 0, "best_streak": 0, "xp": 0, "level": 1, "games": 0, "correct": 0})
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    if not user:
        session.clear()
        return jsonify({"logged_in": False, "username": None, "best_score": 0, "best_streak": 0, "xp": 0, "level": 1, "games": 0, "correct": 0})
    return jsonify({"logged_in": True, "username": user["username"], "best_score": user["best_score"], "best_streak": user["best_streak"], "xp": user["xp"], "level": level_from_xp(user["xp"]), "games": user["games"], "correct": user["correct"]})


@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    if not 3 <= len(username) <= 20 or not username.replace("_", "").isalnum():
        return jsonify({"success": False, "error": "Kullanıcı adı 3-20 karakter olmalı ve sadece harf, sayı, _ içermeli."}), 400
    if len(password) < 4:
        return jsonify({"success": False, "error": "Şifre en az 4 karakter olmalı."}), 400
    try:
        with get_db() as db:
            db.execute("INSERT INTO users(username,password) VALUES(?,?)", (username, generate_password_hash(password)))
            db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "Bu kullanıcı adı zaten kullanılıyor."}), 409
    session["username"] = username
    return jsonify({"success": True, "username": username, "best_score": 0, "best_streak": 0, "xp": 0, "level": 1})


@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"success": False, "error": "Kullanıcı adı veya şifre yanlış."}), 401
    session["username"] = username
    return jsonify({"success": True, "username": username, "best_score": user["best_score"], "best_streak": user["best_streak"], "xp": user["xp"], "level": level_from_xp(user["xp"])})


@app.route("/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


@app.route("/score", methods=["POST"])
def save_score():
    username = session.get("username")
    if not username:
        return jsonify({"saved": False, "best_score": 0, "best_streak": 0, "xp": 0})
    data = request.get_json(silent=True) or {}
    score = max(0, int(data.get("score", 0)))
    streak = max(0, int(data.get("streak", 0)))
    xp_gain = max(0, int(data.get("xp", 0)))
    correct = max(0, int(data.get("correct", 0)))
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if not user:
            session.clear()
            return jsonify({"saved": False}), 401
        best_score = max(user["best_score"], score)
        best_streak = max(user["best_streak"], streak)
        xp = user["xp"] + xp_gain
        games = user["games"] + 1
        total_correct = user["correct"] + correct
        db.execute("UPDATE users SET best_score=?,best_streak=?,xp=?,games=?,correct=? WHERE username=?", (best_score,best_streak,xp,games,total_correct,username))
        db.commit()
    return jsonify({"saved": True, "best_score": best_score, "best_streak": best_streak, "xp": xp, "level": level_from_xp(xp), "new_score_record": score > user["best_score"], "new_streak_record": streak > user["best_streak"]})


if __name__ == "__main__":
    app.run(debug=True)

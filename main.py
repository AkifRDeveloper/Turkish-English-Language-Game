import random

kelimeler = {
    "kolay": [
        ("elma", "apple"), ("ev", "house"), ("araba", "car"),
        ("kitap", "book"), ("su", "water"), ("köpek", "dog"),
        ("kedi", "cat"), ("okul", "school"), ("masa", "table"),
        ("kalem", "pencil")
    ],
    "orta": [
        ("mutlu", "happy"), ("üzgün", "sad"), ("güzel", "beautiful"),
        ("şehir", "city"), ("ülke", "country"), ("öğretmen", "teacher"),
        ("öğrenci", "student"), ("hastane", "hospital"),
        ("kütüphane", "library"), ("bilgisayar", "computer")
    ],
    "zor": [
        ("teknoloji", "technology"), ("üniversite", "university"),
        ("başarı", "success"), ("sorumluluk", "responsibility"),
        ("çevre", "environment"), ("geliştirmek", "develop"),
        ("deneyim", "experience"), ("fırsat", "opportunity"),
        ("bağımsız", "independent"), ("yaratıcılık", "creativity")
    ]
}

def kelime_sec(zorluk):
    return random.choice(kelimeler[zorluk])

print("Kelime Oyunu")
print("----------------")

zorluk = input("Zorluk seçin (kolay/orta/zor): ").lower()

if zorluk not in kelimeler:
    print("Geçersiz zorluk.")
else:
    puan = 0

    for i in range(10):
        turkce, ingilizce = kelime_sec(zorluk)
        print()
        print("Kelime:", turkce)

        cevap = input("İngilizcesini yazın: ").lower().strip()

        if cevap == ingilizce.lower():
            print("Doğru!")
            puan += 1
        else:
            print("Yanlış!")
            print("Doğru cevap:", ingilizce)

    print()
    print("Oyun bitti!")
    print("Skor:", puan, "/ 10")

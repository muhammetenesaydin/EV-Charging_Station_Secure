import os

# İzinli dosya yolu (Yazma izni olan dosya)
allowed_file_path = '/home/gokhan/ev-guvenlik-testleri/venv/bootnotif_allowed.json'

# İzinsiz dosya yolu (Yazma izni olmayan dosya)
denied_file_path = '/home/gokhan/ev-guvenlik-testleri/venv/bootnotif_denied.json'

# Dosyaya yazma fonksiyonu
def write_to_file(file_path, content):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"Başarıyla yazıldı: {file_path}")
    except PermissionError:
        print(f"İzin hatası! Dosyaya yazma izniniz yok: {file_path}")
    except Exception as e:
        print(f"Beklenmedik bir hata oluştu: {e}")

# İzinli dosyaya yazma
print("İzinli dosyaya yazma testi:")
write_to_file(allowed_file_path, "Bu, izinli dosyaya yazılmış bir içeriktir.")

# İzinsiz dosyaya yazma
print("\nİzinsiz dosyaya yazma testi:")
write_to_file(denied_file_path, "Bu, izinsiz dosyaya yazılmaya çalışılan bir içeriktir.")

# Dosyaların varlığını kontrol et (ve içeriklerini de okuyabiliriz)
def check_file_content(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            print(f"\n{file_path} içeriği:")
            print(file.read())
    else:
        print(f"{file_path} bulunamadı.")

# İzinli dosyanın içeriğini kontrol et
check_file_content(allowed_file_path)

# İzinsiz dosyanın içe

# Anomali 3: Aralık Dışı Değer (Out-of-Range Payload)

## Açıklama
Maksimum şarj akımı 80A olması gerekirken 255 Amper gibi fiziksel olarak imkansız veya aralık dışı değerlere sahip CAN mesajlarının gönderilmesini simüle eder.

## Güvenlik Etkisi
- **Saldırı Türü**: Veri Enjeksiyonu / Bozuk Veri
- **Risk Seviyesi**: ORTA-YÜKSEK
- **Etki**: Hatalı davranışa neden olabilir, ekipmana zarar verebilir veya güvenlik sınırlarını aşabilir

## Nasıl Çalışır
1. Saldırgan max_current = 255A olan CAN mesajı gönderir
2. Şarj akımı için normal aralık: 0-80A
3. IDS, payload değerlerini bilinen güvenli aralıklara göre doğrular
4. Aralık dışı değerler için alarm tetiklenir

## Tespit Yöntemi
- Kritik parametreler (akım, voltaj, güç, sıcaklık) için geçerli aralıkları tanımla
- Her CAN mesajı yükünü aralıklara göre doğrula
- Değerler güvenli limitleri aştığında alarm ver

## Testi Çalıştırma
```bash
python anomalies/03_out_of_range_payload/test_scenario.py
```

## Beklenen Çıktı
```
⚠️  ANOMALİ 3: Aralık dışı değer tespit edildi - current: 255 (geçerli aralık: 0-80)
```

## Konfigürasyon
- `can_id`: Akım/voltaj mesajları için CAN ID (varsayılan: 0x400)
- `parameter`: Test edilecek parametre (current, voltage, power, temperature)
- `attack_value`: Gönderilecek aralık dışı değer
- `valid_range`: Parametre için geçerli aralık

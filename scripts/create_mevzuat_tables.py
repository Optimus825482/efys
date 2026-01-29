"""Create mevzuat tracking tables"""
from services.database import DatabaseService

db = DatabaseService()
try:
    # Mevzuat Kaynakları Tablosu
    db.cur.execute("""
    CREATE TABLE IF NOT EXISTS mevzuat_sources (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        url VARCHAR(500) NOT NULL,
        source_type VARCHAR(50) DEFAULT 'web',
        check_interval_hours INTEGER DEFAULT 24,
        last_checked_at TIMESTAMP,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Mevzuat Anahtar Kelimeler Tablosu
    db.cur.execute("""
    CREATE TABLE IF NOT EXISTS mevzuat_keywords (
        id SERIAL PRIMARY KEY,
        keyword VARCHAR(100) NOT NULL,
        priority INTEGER DEFAULT 1,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Mevzuat Uyarıları/Bulunan İçerikler Tablosu
    db.cur.execute("""
    CREATE TABLE IF NOT EXISTS mevzuat_alerts (
        id SERIAL PRIMARY KEY,
        source_id INTEGER REFERENCES mevzuat_sources(id),
        title TEXT NOT NULL,
        url VARCHAR(500),
        content_snippet TEXT,
        matched_keywords TEXT[],
        published_date DATE,
        found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_read BOOLEAN DEFAULT false,
        is_important BOOLEAN DEFAULT false,
        notes TEXT
    )
    """)
    db.conn.commit()
    print('✓ Tablolar oluşturuldu!')

    # Varsayılan kaynakları ekle
    sources = [
        ('Resmi Gazete', 'https://www.resmigazete.gov.tr/', 'rss'),
        ('EPDK Duyurular', 'https://www.epdk.gov.tr/Detay/Icerik/3-0-0/duyurular', 'web'),
        ('EPDK Kurul Kararları', 'https://www.epdk.gov.tr/Detay/Icerik/3-0-21/kurul-kararlari', 'web'),
        ('EPDK Mevzuat', 'https://www.epdk.gov.tr/Detay/Icerik/3-1/elektrik-piyasasi-mevzuati', 'web'),
        ('TEİAŞ Duyurular', 'https://www.teias.gov.tr/tr/duyurular', 'web'),
        ('Mevzuat.gov.tr', 'https://www.mevzuat.gov.tr/', 'web'),
    ]
    for name, url, stype in sources:
        db.cur.execute("""
            INSERT INTO mevzuat_sources (name, url, source_type)
            SELECT %s, %s, %s
            WHERE NOT EXISTS (SELECT 1 FROM mevzuat_sources WHERE url = %s)
        """, (name, url, stype, url))
    db.conn.commit()
    print('✓ Kaynaklar eklendi!')

    # Anahtar kelimeleri ekle
    keywords = [
        ('Elektrik Piyasası', 1),
        ('EPDK', 1),
        ('Dağıtım Bedeli', 1),
        ('Tarife', 1),
        ('OSB', 1),
        ('Organize Sanayi', 1),
        ('Reaktif Enerji', 2),
        ('YEKDEM', 2),
        ('Sayaç', 2),
        ('İletim Bedeli', 2),
        ('Son Kaynak Tedarik', 1),
        ('Tüketici Hizmetleri', 2),
    ]
    for kw, prio in keywords:
        db.cur.execute("""
            INSERT INTO mevzuat_keywords (keyword, priority)
            SELECT %s, %s
            WHERE NOT EXISTS (SELECT 1 FROM mevzuat_keywords WHERE keyword = %s)
        """, (kw, prio, kw))
    db.conn.commit()
    print('✓ Anahtar kelimeler eklendi!')
    
finally:
    db.close()

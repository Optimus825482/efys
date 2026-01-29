"""Billing Routes - PostgreSQL Integrated"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from services.database import DatabaseService
from services import (
    create_invoice,
    bulk_create_invoices,
    preview_invoice,
    cancel_invoice,
    add_additional_item,
    get_invoice_by_id,
    get_invoices_by_period,
    get_unpaid_invoices,
)

billing_bp = Blueprint("billing", __name__)


@billing_bp.route("/")
def index():
    """Faturalama ana sayfası - Gerçek veritabanı metrikleri"""
    db = DatabaseService()
    try:
        # Gerçek operasyonel metrikler (Ödeme takibi YOK)
        stats = {
            "total_invoices": 0,
            "billing_periods": 0,
            "total_subscribers": 0,
            "active_meters": 0,
        }

        # Toplam fatura sayısı
        db.cur.execute("SELECT COUNT(*) as count FROM invoices")
        result = db.cur.fetchone()
        if result:
            stats["total_invoices"] = result["count"]

        # Fatura dönemleri sayısı
        db.cur.execute("SELECT COUNT(*) as count FROM billing_periods")
        result = db.cur.fetchone()
        if result:
            stats["billing_periods"] = result["count"]

        # Toplam abone sayısı
        db.cur.execute("SELECT COUNT(*) as count FROM subscribers WHERE status = 'active'")
        result = db.cur.fetchone()
        if result:
            stats["total_subscribers"] = result["count"]

        # Aktif sayaç sayısı
        db.cur.execute("SELECT COUNT(*) as count FROM meters WHERE status = 'active'")
        result = db.cur.fetchone()
        if result:
            stats["active_meters"] = result["count"]

        return render_template("billing/index.html", stats=stats)
    except Exception as e:
        print(f"Error loading billing index: {e}")
        return render_template("billing/index.html", stats={})
    finally:
        db.close()


@billing_bp.route("/tariff")
def tariff():
    """Tarife yönetimi - Tüm tarife türlerini gösterir"""
    db = DatabaseService()
    try:
        # 1. Enerji Tarifeleri (T1/T2/T3)
        tariffs = db.get_all_tariffs()
        
        # 2. OSB Dağıtım Tarifeleri
        db.cur.execute("""
            SELECT id, period_year, og_rate, ag_rate, capacity_rate, 
                   energy_rate, is_active, epdk_approved
            FROM osb_distribution_tariffs
            ORDER BY period_year DESC
        """)
        osb_tariffs = [dict(row) for row in db.cur.fetchall()]
        
        # 3. EDAŞ Tavan Tarifeleri
        db.cur.execute("""
            SELECT id, edas_name, single_term_og_rate, single_term_ag_rate,
                   dual_term_capacity_rate, dual_term_energy_rate, 
                   valid_from, valid_to, is_active
            FROM edas_tariffs
            ORDER BY edas_name
        """)
        edas_tariffs = [dict(row) for row in db.cur.fetchall()]
        
        # 4. OSB Faturalama Ayarları (key-value formatında)
        db.cur.execute("""
            SELECT setting_key, setting_value 
            FROM osb_billing_settings 
            WHERE valid_to IS NULL OR valid_to >= CURRENT_DATE
        """)
        settings = {row['setting_key']: float(row['setting_value']) for row in db.cur.fetchall()}
        
        return render_template(
            "billing/tariff.html", 
            tariffs=tariffs,
            osb_tariffs=osb_tariffs,
            edas_tariffs=edas_tariffs,
            settings=settings
        )
    except Exception as e:
        print(f"Error loading tariffs: {e}")
        import traceback
        traceback.print_exc()
        return render_template("billing/tariff.html", tariffs=[], osb_tariffs=[], edas_tariffs=[], settings={})
    finally:
        db.close()


@billing_bp.route("/period")
def period():
    """Fatura dönemleri"""
    db = DatabaseService()
    try:
        periods = db.get_billing_periods_with_stats()
        return render_template("billing/period.html", periods=periods)
    except Exception as e:
        print(f"Error loading billing periods: {e}")
        return render_template("billing/period.html", periods=[])
    finally:
        db.close()


@billing_bp.route("/calculate")
def calculate():
    """Fatura hesaplama"""
    db = DatabaseService()
    try:
        subscribers = db.get_all_subscribers()
        periods = db.get_billing_periods()
        tariffs = db.get_tariffs()
        return render_template(
            "billing/calculate.html",
            subscribers=subscribers,
            periods=periods,
            tariffs=tariffs,
        )
    except Exception as e:
        print(f"Error loading calculation data: {e}")
        return render_template(
            "billing/calculate.html", subscribers=[], periods=[], tariffs=[]
        )
    finally:
        db.close()


@billing_bp.route("/bulk")
def bulk_invoice():
    """Toplu fatura oluşturma sayfası"""
    db = DatabaseService()
    try:
        periods = db.get_billing_periods()
        tariffs = db.get_tariffs()
        
        # Özet istatistikler - Abone sayısı ayrı, tüketim ayrı sorgulanmalı
        db.cur.execute("SELECT COUNT(*) as total_subscribers FROM subscribers")
        subscriber_count = db.cur.fetchone()['total_subscribers']
        
        db.cur.execute("""
            SELECT COALESCE(SUM(r.total_consumption), 0)::bigint as total_consumption
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            WHERE r.reading_time >= DATE_TRUNC('month', CURRENT_DATE)
        """)
        consumption_row = db.cur.fetchone()
        total_consumption = consumption_row['total_consumption'] if consumption_row else 0
        
        # Sektör dağılımı
        db.cur.execute("""
            SELECT sector, COUNT(*) as count 
            FROM subscribers 
            WHERE sector IS NOT NULL 
            GROUP BY sector 
            ORDER BY count DESC
        """)
        sectors = [dict(r) for r in db.cur.fetchall()]
        
        stats = {
            'total_subscribers': subscriber_count,
            'total_consumption': total_consumption,
            'estimated_amount': (total_consumption or 0) * 3.5,  # Ortalama birim fiyat
            'sectors': sectors
        }
        
        return render_template("billing/bulk-invoice.html", 
                             periods=periods, 
                             tariffs=tariffs,
                             stats=stats)
    except Exception as e:
        print(f"Error loading bulk invoice page: {e}")
        import traceback
        traceback.print_exc()
        return render_template("billing/bulk-invoice.html", 
                             periods=[], 
                             tariffs=[],
                             stats={'total_subscribers': 0, 'total_consumption': 0, 'estimated_amount': 0, 'sectors': []})
    finally:
        db.close()



@billing_bp.route("/preview")
@billing_bp.route("/preview/<int:subscriber_id>/<int:period_id>")
def preview(subscriber_id=None, period_id=None):
    """Fatura önizleme"""
    if not subscriber_id or not period_id:
        return render_template("billing/preview.html", invoice=None)

    try:
        invoice_data = preview_invoice(subscriber_id, period_id)
        return render_template("billing/preview.html", invoice=invoice_data)
    except Exception as e:
        print(f"Error previewing invoice: {e}")
        flash(f"Fatura önizleme hatası: {str(e)}", "error")
        return render_template("billing/preview.html", invoice=None)


@billing_bp.route("/additional")
def additional():
    """Ek kalemler sayfası"""
    db = DatabaseService()
    try:
        # Aboneler
        subscribers = db.get_all_subscribers()
        
        # Son 50 fatura
        db.cur.execute("""
            SELECT 
                i.id, i.invoice_no, i.invoice_date,
                s.subscriber_code, s.name as subscriber_name,
                i.total_amount, i.status
            FROM invoices i
            JOIN subscribers s ON i.subscriber_id = s.id
            ORDER BY i.invoice_date DESC
            LIMIT 50
        """)
        invoices = [dict(row) for row in db.cur.fetchall()]

        return render_template("billing/additional.html", 
                             invoices=invoices,
                             subscribers=subscribers)
    except Exception as e:
        print(f"Error loading additional items page: {e}")
        return render_template("billing/additional.html", invoices=[], subscribers=[])
    finally:
        db.close()


@billing_bp.route("/cancel")
def cancel():
    """Fatura iptali sayfası"""
    db = DatabaseService()
    try:
        # İptal edilebilir faturalar (draft veya issued)
        db.cur.execute("""
            SELECT 
                i.id, i.invoice_no, i.invoice_date,
                s.subscriber_code, s.name as subscriber_name,
                i.total_amount, i.status
            FROM invoices i
            JOIN subscribers s ON i.subscriber_id = s.id
            WHERE i.status IN ('draft', 'issued')
            ORDER BY i.invoice_date DESC
        """)
        invoices = [dict(row) for row in db.cur.fetchall()]

        return render_template("billing/cancel.html", invoices=invoices)
    except Exception as e:
        print(f"Error loading cancel page: {e}")
        return render_template("billing/cancel.html", invoices=[])
    finally:
        db.close()


@billing_bp.route("/print")
@billing_bp.route("/print/<int:invoice_id>")
def print_invoice(invoice_id=None):
    """Fatura yazdırma"""
    if not invoice_id:
        return render_template("billing/print.html", invoice=None)

    try:
        invoice = get_invoice_by_id(invoice_id)
        return render_template("billing/print.html", invoice=invoice)
    except Exception as e:
        print(f"Error loading invoice for print: {e}")
        return render_template("billing/print.html", invoice=None)


# =============================================================================
# API ENDPOINTS
# =============================================================================


@billing_bp.route("/api/create-invoice", methods=["POST"])
def api_create_invoice():
    """API: Fatura oluştur"""
    try:
        data = request.get_json()
        subscriber_id = data.get("subscriber_id")
        period_id = data.get("period_id")
        tariff_id = data.get("tariff_id")

        if not all([subscriber_id, period_id, tariff_id]):
            return jsonify(
                {
                    "success": False,
                    "error": "subscriber_id, period_id ve tariff_id gerekli",
                }
            ), 400

        invoice = create_invoice(subscriber_id, period_id, tariff_id)

        return jsonify(
            {
                "success": True,
                "data": invoice,
                "message": "Fatura başarıyla oluşturuldu",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@billing_bp.route("/api/bulk-create", methods=["POST"])
def api_bulk_create():
    """API: Toplu fatura oluşturma"""
    try:
        data = request.get_json()
        period_id = data.get("period_id")

        if not period_id:
            return jsonify({"success": False, "error": "period_id gerekli"}), 400

        result = bulk_create_invoices(period_id)

        return jsonify(
            {
                "success": True,
                "data": result,
                "message": f"{result['success_count']} fatura oluşturuldu",
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@billing_bp.route("/api/cancel/<int:invoice_id>", methods=["POST"])
def api_cancel_invoice(invoice_id):
    """API: Fatura iptali"""
    try:
        data = request.get_json()
        reason = data.get("reason", "Kullanıcı talebi")

        result = cancel_invoice(invoice_id, reason)

        return jsonify(
            {"success": True, "data": result, "message": "Fatura iptal edildi"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@billing_bp.route("/api/additional/<int:invoice_id>", methods=["POST"])
def api_add_additional(invoice_id):
    """API: Ek kalem ekleme"""
    try:
        data = request.get_json()
        description = data.get("description")
        amount = data.get("amount")

        if not all([description, amount]):
            return jsonify(
                {"success": False, "error": "description ve amount gerekli"}
            ), 400

        result = add_additional_item(invoice_id, description, float(amount))

        return jsonify({"success": True, "data": result, "message": "Ek kalem eklendi"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@billing_bp.route("/api/invoices/period/<int:period_id>")
def api_invoices_by_period(period_id):
    """API: Döneme göre faturalar"""
    try:
        invoices = get_invoices_by_period(period_id)
        return jsonify({"success": True, "data": invoices})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@billing_bp.route("/api/invoices/unpaid")
def api_unpaid_invoices():
    """API: Ödenmemiş faturalar"""
    try:
        invoices = get_unpaid_invoices()
        return jsonify({"success": True, "data": invoices})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@billing_bp.route("/api/periods")
def api_periods():
    """API: Fatura dönemleri listesi"""
    db = DatabaseService()
    try:
        periods = db.get_billing_periods()
        return jsonify({"success": True, "data": periods})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


# =============================================================================
# TARİFE YÖNETİMİ API ENDPOINTS
# EPDK Dağıtım Tarifesi Tebliği uyumlu tarife CRUD operasyonları
# =============================================================================

@billing_bp.route("/api/tariffs", methods=["GET"])
def api_get_tariffs():
    """API: Tüm enerji tarifelerini getir"""
    db = DatabaseService()
    try:
        tariffs = db.get_all_tariffs()
        return jsonify({"success": True, "data": tariffs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@billing_bp.route("/api/tariffs", methods=["POST"])
def api_create_tariff():
    """API: Yeni enerji tarifesi oluştur"""
    db = DatabaseService()
    try:
        data = request.get_json()
        
        # Validasyon
        required = ["name", "tariff_type", "t1_rate", "t2_rate", "t3_rate"]
        for field in required:
            if field not in data:
                return jsonify({"success": False, "error": f"{field} gerekli"}), 400
        
        db.cur.execute("""
            INSERT INTO tariffs (name, tariff_type, t1_rate, t2_rate, t3_rate, 
                                reactive_rate, distribution_fee, epdk_limit, 
                                valid_from, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_DATE, true)
            RETURNING id
        """, (
            data["name"],
            data["tariff_type"],
            data["t1_rate"],
            data["t2_rate"],
            data["t3_rate"],
            data.get("reactive_rate", 0),
            data.get("distribution_fee", 0),
            data.get("epdk_limit", 4.25)
        ))
        
        new_id = db.cur.fetchone()["id"]
        db.conn.commit()
        
        return jsonify({
            "success": True, 
            "data": {"id": new_id},
            "message": "Tarife başarıyla oluşturuldu"
        }), 201
        
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@billing_bp.route("/api/tariffs/<int:tariff_id>", methods=["PUT"])
def api_update_tariff(tariff_id):
    """API: Enerji tarifesi güncelle"""
    db = DatabaseService()
    try:
        data = request.get_json()
        
        db.cur.execute("""
            UPDATE tariffs SET
                name = COALESCE(%s, name),
                tariff_type = COALESCE(%s, tariff_type),
                t1_rate = COALESCE(%s, t1_rate),
                t2_rate = COALESCE(%s, t2_rate),
                t3_rate = COALESCE(%s, t3_rate),
                reactive_rate = COALESCE(%s, reactive_rate),
                distribution_fee = COALESCE(%s, distribution_fee),
                epdk_limit = COALESCE(%s, epdk_limit),
                is_active = COALESCE(%s, is_active)
            WHERE id = %s
            RETURNING id
        """, (
            data.get("name"),
            data.get("tariff_type"),
            data.get("t1_rate"),
            data.get("t2_rate"),
            data.get("t3_rate"),
            data.get("reactive_rate"),
            data.get("distribution_fee"),
            data.get("epdk_limit"),
            data.get("is_active"),
            tariff_id
        ))
        
        result = db.cur.fetchone()
        if not result:
            return jsonify({"success": False, "error": "Tarife bulunamadı"}), 404
            
        db.conn.commit()
        return jsonify({"success": True, "message": "Tarife güncellendi"})
        
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@billing_bp.route("/api/tariffs/<int:tariff_id>", methods=["DELETE"])
def api_delete_tariff(tariff_id):
    """API: Enerji tarifesi sil (soft delete - pasifleştir)"""
    db = DatabaseService()
    try:
        db.cur.execute("""
            UPDATE tariffs SET is_active = false, valid_to = CURRENT_DATE
            WHERE id = %s RETURNING id
        """, (tariff_id,))
        
        result = db.cur.fetchone()
        if not result:
            return jsonify({"success": False, "error": "Tarife bulunamadı"}), 404
            
        db.conn.commit()
        return jsonify({"success": True, "message": "Tarife pasifleştirildi"})
        
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


# =============================================================================
# OSB DAĞITIM TARİFELERİ API
# EPDK Dağıtım Gelir Gereksinimi (DGG) formülasyonuna uygun
# =============================================================================

@billing_bp.route("/api/osb-distribution-tariffs", methods=["GET"])
def api_get_osb_tariffs():
    """API: OSB dağıtım tarifelerini getir"""
    db = DatabaseService()
    try:
        db.cur.execute("""
            SELECT id, period_year, og_rate, ag_rate, capacity_rate, 
                   energy_rate, is_active, epdk_approved, edas_tariff_id
            FROM osb_distribution_tariffs
            ORDER BY period_year DESC
        """)
        tariffs = [dict(row) for row in db.cur.fetchall()]
        return jsonify({"success": True, "data": tariffs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@billing_bp.route("/api/osb-distribution-tariffs", methods=["POST"])
def api_create_osb_tariff():
    """API: Yeni OSB dağıtım tarifesi oluştur"""
    db = DatabaseService()
    try:
        data = request.get_json()
        
        # Validasyon
        if "period_year" not in data:
            return jsonify({"success": False, "error": "period_year gerekli"}), 400
        
        db.cur.execute("""
            INSERT INTO osb_distribution_tariffs 
                (period_year, og_rate, ag_rate, capacity_rate, energy_rate, is_active)
            VALUES (%s, %s, %s, %s, %s, true)
            RETURNING id
        """, (
            data["period_year"],
            data.get("og_rate", 25.00),
            data.get("ag_rate", 30.00),
            data.get("capacity_rate", 0),
            data.get("energy_rate", 0)
        ))
        
        new_id = db.cur.fetchone()["id"]
        db.conn.commit()
        
        return jsonify({
            "success": True, 
            "data": {"id": new_id},
            "message": "OSB dağıtım tarifesi oluşturuldu"
        }), 201
        
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@billing_bp.route("/api/osb-distribution-tariffs/<int:tariff_id>", methods=["PUT"])
def api_update_osb_tariff(tariff_id):
    """API: OSB dağıtım tarifesi güncelle - EDAŞ tavan kontrolü yapılır"""
    db = DatabaseService()
    try:
        data = request.get_json()
        
        # EDAŞ tavan kontrolü
        og_rate = data.get("og_rate")
        ag_rate = data.get("ag_rate")
        
        if og_rate or ag_rate:
            db.cur.execute("SELECT single_term_og_rate, single_term_ag_rate FROM edas_tariffs LIMIT 1")
            edas = db.cur.fetchone()
            if edas:
                if og_rate and float(og_rate) > float(edas["single_term_og_rate"]):
                    return jsonify({
                        "success": False, 
                        "error": f"OG rate ({og_rate}) EDAŞ tavanını ({edas['single_term_og_rate']}) aşamaz!"
                    }), 400
                if ag_rate and float(ag_rate) > float(edas["single_term_ag_rate"]):
                    return jsonify({
                        "success": False, 
                        "error": f"AG rate ({ag_rate}) EDAŞ tavanını ({edas['single_term_ag_rate']}) aşamaz!"
                    }), 400
        
        db.cur.execute("""
            UPDATE osb_distribution_tariffs SET
                og_rate = COALESCE(%s, og_rate),
                ag_rate = COALESCE(%s, ag_rate),
                capacity_rate = COALESCE(%s, capacity_rate),
                energy_rate = COALESCE(%s, energy_rate),
                is_active = COALESCE(%s, is_active)
            WHERE id = %s
            RETURNING id
        """, (
            og_rate,
            ag_rate,
            data.get("capacity_rate"),
            data.get("energy_rate"),
            data.get("is_active"),
            tariff_id
        ))
        
        result = db.cur.fetchone()
        if not result:
            return jsonify({"success": False, "error": "Tarife bulunamadı"}), 404
            
        db.conn.commit()
        return jsonify({"success": True, "message": "OSB dağıtım tarifesi güncellendi"})
        
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


# =============================================================================
# EDAŞ TAVAN TARİFELERİ API
# Bölgesel elektrik dağıtım şirketi tavan bedelleri
# =============================================================================

@billing_bp.route("/api/edas-tariffs", methods=["GET"])
def api_get_edas_tariffs():
    """API: EDAŞ tavan tarifelerini getir"""
    db = DatabaseService()
    try:
        db.cur.execute("""
            SELECT id, edas_name, single_term_og_rate, single_term_ag_rate,
                   dual_term_capacity_rate, dual_term_energy_rate, 
                   valid_from, valid_to, is_active
            FROM edas_tariffs
            ORDER BY edas_name
        """)
        tariffs = [dict(row) for row in db.cur.fetchall()]
        return jsonify({"success": True, "data": tariffs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@billing_bp.route("/api/edas-tariffs", methods=["POST"])
def api_create_edas_tariff():
    """API: Yeni EDAŞ tavan tarifesi oluştur"""
    db = DatabaseService()
    try:
        data = request.get_json()
        
        if "edas_name" not in data:
            return jsonify({"success": False, "error": "edas_name gerekli"}), 400
        
        db.cur.execute("""
            INSERT INTO edas_tariffs 
                (edas_name, single_term_og_rate, single_term_ag_rate,
                 dual_term_capacity_rate, dual_term_energy_rate, valid_from)
            VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
            RETURNING id
        """, (
            data["edas_name"],
            data.get("single_term_og_rate", 32.50),
            data.get("single_term_ag_rate", 38.75),
            data.get("dual_term_capacity_rate", 4500),
            data.get("dual_term_energy_rate", 18.50)
        ))
        
        new_id = db.cur.fetchone()["id"]
        db.conn.commit()
        
        return jsonify({
            "success": True, 
            "data": {"id": new_id},
            "message": "EDAŞ tarifesi oluşturuldu"
        }), 201
        
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


# =============================================================================
# FATURALAMA AYARLARI API
# KDV, BTV, iletim, reaktif ceza oranları
# =============================================================================

@billing_bp.route("/api/billing-settings", methods=["GET"])
def api_get_billing_settings():
    """API: Faturalama ayarlarını getir (key-value formatında)"""
    db = DatabaseService()
    try:
        db.cur.execute("""
            SELECT setting_key, setting_value, description 
            FROM osb_billing_settings 
            WHERE valid_to IS NULL OR valid_to >= CURRENT_DATE
            ORDER BY setting_key
        """)
        rows = db.cur.fetchall()
        # Key-value formatına dönüştür
        settings = {row['setting_key']: float(row['setting_value']) for row in rows}
        return jsonify({"success": True, "data": settings})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@billing_bp.route("/api/billing-settings", methods=["PUT"])
def api_update_billing_settings():
    """API: Faturalama ayarlarını güncelle (key-value formatında)"""
    db = DatabaseService()
    try:
        data = request.get_json()
        
        # Her key için update veya insert yap
        for key, value in data.items():
            db.cur.execute("""
                UPDATE osb_billing_settings 
                SET setting_value = %s, updated_at = CURRENT_TIMESTAMP
                WHERE setting_key = %s AND (valid_to IS NULL OR valid_to >= CURRENT_DATE)
            """, (value, key))
            
            # Eğer update etmediyse insert et
            if db.cur.rowcount == 0:
                db.cur.execute("""
                    INSERT INTO osb_billing_settings (setting_key, setting_value, valid_from)
                    VALUES (%s, %s, CURRENT_DATE)
                """, (key, value))
        
        db.conn.commit()
        return jsonify({"success": True, "message": "Faturalama ayarları güncellendi"})
        
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@billing_bp.route("/api/calculate", methods=["GET"])
def api_calculate():
    """API: Fatura hesapla (tekil veya toplu)"""
    from services.database import calculate_invoice
    
    db = DatabaseService()
    try:
        period_id = request.args.get("period_id", type=int)
        subscriber_id = request.args.get("subscriber_id", type=int)
        
        if not period_id:
            return jsonify({"success": False, "error": "Dönem seçilmedi"}), 400
        
        # Tekil hesaplama
        if subscriber_id:
            result = _calculate_subscriber(db, subscriber_id, period_id)
            if not result:
                return jsonify({"success": False, "error": "Hesaplama yapılamadı"}), 400
            return jsonify({"success": True, "data": result})
        
        # Toplu hesaplama
        subscribers = db.get_all_subscribers()
        results = []
        
        for sub in subscribers:
            try:
                result = _calculate_subscriber(db, sub['id'], period_id)
                if result:
                    result['status'] = 'ok'
                    results.append(result)
                else:
                    results.append({
                        'subscriber_id': sub['id'],
                        'subscriber_code': sub['subscriber_code'],
                        'subscriber_name': sub['name'],
                        'status': 'no_data',
                        't1_consumption': 0,
                        't2_consumption': 0,
                        't3_consumption': 0,
                        'total_amount': 0
                    })
            except Exception as e:
                results.append({
                    'subscriber_id': sub['id'],
                    'subscriber_code': sub['subscriber_code'],
                    'subscriber_name': sub['name'],
                    'status': 'error',
                    'error': str(e),
                    't1_consumption': 0,
                    't2_consumption': 0,
                    't3_consumption': 0,
                    'total_amount': 0
                })
        
        return jsonify({"success": True, "data": results})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


def _calculate_subscriber(db, subscriber_id, period_id):
    """Tekil abone için fatura hesaplama"""
    # Dönem bilgisi
    db.cur.execute("SELECT * FROM billing_periods WHERE id = %s", (period_id,))
    period = db.cur.fetchone()
    if not period:
        return None
    
    # Abone + tarife bilgisi
    db.cur.execute("""
        SELECT s.id, s.subscriber_code, s.name, s.tariff_id,
               t.name as tariff_name, t.t1_rate, t.t2_rate, t.t3_rate, t.reactive_rate
        FROM subscribers s
        LEFT JOIN tariffs t ON s.tariff_id = t.id
        WHERE s.id = %s
    """, (subscriber_id,))
    subscriber = db.cur.fetchone()
    if not subscriber:
        return None
    
    # Sayaç ID
    db.cur.execute("SELECT id FROM meters WHERE subscriber_id = %s LIMIT 1", (subscriber_id,))
    meter = db.cur.fetchone()
    if not meter:
        return None
    
    # Tüketim hesapla
    db.cur.execute("""
        SELECT 
            COALESCE(SUM(t1_consumption), 0) as t1,
            COALESCE(SUM(t2_consumption), 0) as t2,
            COALESCE(SUM(t3_consumption), 0) as t3,
            COALESCE(SUM(total_consumption), 0) as total,
            COALESCE(SUM(inductive_reactive), 0) as inductive,
            COALESCE(SUM(capacitive_reactive), 0) as capacitive,
            COALESCE(MAX(max_demand), 0) as max_demand
        FROM readings
        WHERE meter_id = %s
        AND reading_time >= %s AND reading_time < %s
    """, (meter['id'], period['period_start'], period['period_end']))
    consumption = db.cur.fetchone()
    
    t1 = float(consumption['t1'] or 0)
    t2 = float(consumption['t2'] or 0)
    t3 = float(consumption['t3'] or 0)
    total_kwh = t1 + t2 + t3
    
    # Tarife oranları
    t1_rate = float(subscriber.get('t1_rate') or 0)
    t2_rate = float(subscriber.get('t2_rate') or 0)
    t3_rate = float(subscriber.get('t3_rate') or 0)
    reactive_rate = float(subscriber.get('reactive_rate') or 0)
    
    # Enerji tutarları
    t1_amount = t1 * t1_rate
    t2_amount = t2 * t2_rate
    t3_amount = t3 * t3_rate
    
    # Dağıtım bedeli (~0.25 TL/kWh varsayılan)
    distribution_rate = 0.25
    distribution_amount = total_kwh * distribution_rate
    
    # Reaktif hesabı
    reactive_penalty = 0
    cos_phi = 1.0
    inductive = float(consumption['inductive'] or 0)
    capacitive = float(consumption['capacitive'] or 0)
    total_reactive = inductive + capacitive
    
    if total_kwh > 0 and total_reactive > 0:
        tan_phi = total_reactive / total_kwh
        cos_phi = 1 / ((1 + tan_phi**2) ** 0.5)
        if cos_phi < 0.90:  # EPDK sınırı
            allowed_reactive = total_kwh * 0.484  # tan(arccos(0.9))
            excess_reactive = total_reactive - allowed_reactive
            if excess_reactive > 0:
                reactive_penalty = excess_reactive * reactive_rate
    
    # Ara toplam
    subtotal = t1_amount + t2_amount + t3_amount + distribution_amount + reactive_penalty
    
    # Vergiler
    otv_rate = 0.05
    kdv_rate = 0.20
    otv_amount = subtotal * otv_rate
    kdv_amount = (subtotal + otv_amount) * kdv_rate
    total_amount = subtotal + otv_amount + kdv_amount
    
    return {
        'subscriber_id': subscriber['id'],
        'subscriber_code': subscriber['subscriber_code'],
        'subscriber_name': subscriber['name'],
        'period_id': period_id,
        't1_consumption': round(t1, 2),
        't2_consumption': round(t2, 2),
        't3_consumption': round(t3, 2),
        'total_consumption': round(total_kwh, 2),
        'max_demand': round(float(consumption['max_demand'] or 0), 2),
        't1_rate': t1_rate,
        't2_rate': t2_rate,
        't3_rate': t3_rate,
        't1_amount': round(t1_amount, 2),
        't2_amount': round(t2_amount, 2),
        't3_amount': round(t3_amount, 2),
        'distribution_rate': distribution_rate,
        'distribution_amount': round(distribution_amount, 2),
        'reactive_amount': round(total_reactive, 2),
        'cos_phi': round(cos_phi, 3),
        'reactive_penalty': round(reactive_penalty, 2),
        'subtotal': round(subtotal, 2),
        'otv_amount': round(otv_amount, 2),
        'kdv_amount': round(kdv_amount, 2),
        'total_amount': round(total_amount, 2)
    }


@billing_bp.route("/api/create-bulk-invoices", methods=["POST"])
def api_create_bulk_invoices():
    """API: Toplu fatura oluşturma"""
    db = DatabaseService()
    try:
        data = request.get_json()
        period_id = data.get('period_id')
        subscriber_ids = data.get('subscriber_ids', [])
        
        if not period_id:
            return jsonify({"success": False, "error": "Dönem seçilmedi"}), 400
        
        if not subscriber_ids:
            return jsonify({"success": False, "error": "Abone seçilmedi"}), 400
        
        created = 0
        errors = []
        
        for sub_id in subscriber_ids:
            try:
                result = create_invoice(sub_id, period_id)
                if result:
                    created += 1
            except Exception as e:
                errors.append(f"Abone {sub_id}: {str(e)}")
        
        db.conn.commit()
        
        return jsonify({
            "success": True,
            "created": created,
            "errors": errors if errors else None
        })
        
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@billing_bp.route("/api/invoices/subscriber/<int:subscriber_id>")
def api_invoices_by_subscriber(subscriber_id):
    """API: Aboneye ait faturalar"""
    db = DatabaseService()
    try:
        db.cur.execute("""
            SELECT id, invoice_no, invoice_date, total_amount, status
            FROM invoices
            WHERE subscriber_id = %s
            ORDER BY invoice_date DESC
            LIMIT 20
        """, (subscriber_id,))
        invoices = [dict(row) for row in db.cur.fetchall()]
        return jsonify({"success": True, "data": invoices})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@billing_bp.route("/api/periods", methods=["POST"])
def api_create_period():
    """API: Yeni dönem oluştur"""
    db = DatabaseService()
    try:
        data = request.get_json()
        name = data.get('name')
        period_start = data.get('period_start')
        period_end = data.get('period_end')
        status = data.get('status', 'open')
        
        db.cur.execute("""
            INSERT INTO billing_periods (name, period_start, period_end, status)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (name, period_start, period_end, status))
        
        period_id = db.cur.fetchone()['id']
        db.conn.commit()
        
        return jsonify({"success": True, "id": period_id})
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@billing_bp.route("/api/periods/<int:period_id>", methods=["PUT"])
def api_update_period(period_id):
    """API: Dönem güncelle"""
    db = DatabaseService()
    try:
        data = request.get_json()
        
        updates = []
        values = []
        
        if 'name' in data:
            updates.append("name = %s")
            values.append(data['name'])
        if 'status' in data:
            updates.append("status = %s")
            values.append(data['status'])
        if 'period_start' in data:
            updates.append("period_start = %s")
            values.append(data['period_start'])
        if 'period_end' in data:
            updates.append("period_end = %s")
            values.append(data['period_end'])
        
        if updates:
            values.append(period_id)
            db.cur.execute(f"""
                UPDATE billing_periods 
                SET {', '.join(updates)}
                WHERE id = %s
            """, values)
            db.conn.commit()
        
        return jsonify({"success": True})
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


# =========================================================================
# TARIFF MANAGEMENT API ENDPOINTS
# =========================================================================

@billing_bp.route("/api/tariffs", methods=["POST"])
def create_tariff_api():
    """Create new energy tariff"""
    db = DatabaseService()
    try:
        data = request.get_json()
        tariff_id = db.create_tariff(data)
        return jsonify({"success": True, "id": tariff_id})
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@billing_bp.route("/api/tariffs/<int:tariff_id>", methods=["PUT"])
def update_tariff_api(tariff_id):
    """Update energy tariff"""
    db = DatabaseService()
    try:
        data = request.get_json()
        success = db.update_tariff(tariff_id, data)
        return jsonify({"success": success})
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@billing_bp.route("/api/tariffs/<int:tariff_id>", methods=["DELETE"])
def delete_tariff_api(tariff_id):
    """Soft delete energy tariff"""
    db = DatabaseService()
    try:
        success = db.delete_tariff(tariff_id)
        return jsonify({"success": success})
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@billing_bp.route("/api/osb-distribution-tariffs", methods=["POST"])
def create_osb_distribution_tariff_api():
    """Create OSB distribution tariff"""
    db = DatabaseService()
    try:
        data = request.get_json()
        tariff_id = db.create_osb_distribution_tariff(data)
        return jsonify({"success": True, "id": tariff_id})
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@billing_bp.route("/api/edas-tariffs", methods=["POST"])
def create_edas_tariff_api():
    """Create EDAŞ ceiling tariff"""
    db = DatabaseService()
    try:
        data = request.get_json()
        tariff_id = db.create_edas_tariff(data)
        return jsonify({"success": True, "id": tariff_id})
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@billing_bp.route("/api/billing-settings", methods=["PUT"])
def update_billing_settings_api():
    """Update OSB billing settings"""
    db = DatabaseService()
    try:
        data = request.get_json()
        success = db.update_billing_settings(data)
        return jsonify({"success": success})
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

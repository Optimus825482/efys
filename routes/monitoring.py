"""Monitoring Routes - PostgreSQL Integrated"""

from flask import Blueprint, render_template
from services.database import DatabaseService

monitoring_bp = Blueprint("monitoring", __name__)


@monitoring_bp.route("/")
def index():
    return render_template("monitoring/index.html")


@monitoring_bp.route("/last-indexes")
def last_indexes():
    """Son endeksler sayfası"""
    db = DatabaseService()
    try:
        indexes = db.get_meter_indexes()
        stats = db.get_meter_stats()
        return render_template(
            "monitoring/last_indexes.html", indexes=indexes, stats=stats
        )
    except Exception as e:
        print(f"Error loading last indexes: {e}")
        return render_template("monitoring/last_indexes.html", indexes=[], stats=None)
    finally:
        db.close()


@monitoring_bp.route("/load-profile")
def load_profile():
    """Yük profili sayfası"""
    db = DatabaseService()
    try:
        profile = db.get_load_profile()
        demand_stats = db.get_demand_stats()
        return render_template(
            "monitoring/load_profile.html", profile=profile, demand_stats=demand_stats
        )
    except Exception as e:
        print(f"Error loading load profile: {e}")
        return render_template(
            "monitoring/load_profile.html", profile=[], demand_stats=None
        )
    finally:
        db.close()


@monitoring_bp.route("/vee")
def vee():
    """VEE doğrulama sayfası"""
    db = DatabaseService()
    try:
        vee_stats = db.get_vee_data()
        corrections = db.get_vee_corrections()
        trend = db.get_daily_reading_trend(days=7)
        return render_template(
            "monitoring/vee.html",
            vee_stats=vee_stats,
            corrections=corrections,
            trend=trend,
        )
    except Exception as e:
        print(f"Error loading VEE data: {e}")
        return render_template(
            "monitoring/vee.html", vee_stats=None, corrections=[], trend=[]
        )
    finally:
        db.close()


@monitoring_bp.route("/missing-data")
def missing_data():
    """Eksik veri sayfası"""
    from services import get_missing_data, get_missing_data_stats

    try:
        missing = get_missing_data()
        stats_data = get_missing_data_stats()

        stats = {
            "total_missing": stats_data["missing"],
            "critical": len([m for m in missing if m.get("priority") == "high"]),
            "estimated": len([m for m in missing if m.get("estimated")]),
        }

        return render_template(
            "monitoring/missing-data.html", missing=missing, stats=stats
        )

    except Exception as e:
        print(f"Error loading missing data: {e}")
        return render_template("monitoring/missing-data.html", missing=[], stats=None)


@monitoring_bp.route("/loss-analysis")
def loss_analysis():
    """Kayıp/kaçak analizi sayfası - OSB modeli"""
    db = DatabaseService()
    try:
        # OSB kayıp raporu (ana sayaç vs Aboneler) - Aynı veri kaynağı
        report = db.get_osb_loss_report()
        return render_template(
            "monitoring/loss-analysis.html",
            report=report
        )
    except Exception as e:
        print(f"Error loading loss analysis: {e}")
        import traceback
        traceback.print_exc()
        return render_template("monitoring/loss-analysis.html", report=None)
    finally:
        db.close()


# =============================================================================
# API ENDPOINTS
# =============================================================================


@monitoring_bp.route("/api/missing-data")
def api_missing_data():
    """API: Eksik veri listesi"""
    from services import get_missing_data

    try:
        missing = get_missing_data()
        return jsonify({"success": True, "data": missing})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@monitoring_bp.route("/api/estimate", methods=["POST"])
def api_estimate():
    """API: Eksik veri tahmini"""
    from services import estimate_missing_data
    from flask import request

    try:
        data = request.get_json()
        meter_id = data.get("meter_id")
        missing_date = data.get("missing_date")

        if not all([meter_id, missing_date]):
            return jsonify(
                {"success": False, "error": "meter_id ve missing_date gerekli"}
            ), 400

        result = estimate_missing_data(meter_id, missing_date)

        return jsonify(
            {"success": True, "data": result, "message": "Veri tahmini yapıldı"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

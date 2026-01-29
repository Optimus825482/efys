"""Reports Routes - PostgreSQL Integrated"""
from flask import Blueprint, render_template, request
from services.database import DatabaseService

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
def index():
    return render_template('reports/index.html')

@reports_bp.route('/index-report')
def index_report():
    """Endeks raporu"""
    db = DatabaseService()
    try:
        # Son endeksler
        indexes = db.get_meter_indexes()
        stats = db.get_meter_stats()
        
        return render_template('reports/index_report.html', 
                             indexes=indexes,
                             stats=stats)
    except Exception as e:
        print(f"Error loading index report: {e}")
        return render_template('reports/index_report.html', indexes=[], stats=None)
    finally:
        db.close()

@reports_bp.route('/consumption')
def consumption():
    """Tüketim raporu"""
    db = DatabaseService()
    try:
        # Tarih parametreleri
        from datetime import datetime, timedelta
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        sector = request.args.get('sector')
        
        # Varsayılan tarihler
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = datetime(2026, 1, 1).date()
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = datetime(2026, 1, 29).date()
        
        report = db.get_consumption_report(start_date, end_date)
        
        # Sektör listesi için
        db.cur.execute("SELECT DISTINCT sector FROM subscribers WHERE sector IS NOT NULL ORDER BY sector")
        sectors = [r['sector'] for r in db.cur.fetchall()]
        
        return render_template('reports/consumption.html', 
                             report=report,
                             start_date=start_date.strftime('%Y-%m-%d'),
                             end_date=end_date.strftime('%Y-%m-%d'),
                             selected_sector=sector,
                             sectors=sectors)
    except Exception as e:
        print(f"Error loading consumption report: {e}")
        import traceback
        traceback.print_exc()
        return render_template('reports/consumption.html', report=None, sectors=[])
    finally:
        db.close()


# =============================================================================
# EXPORT ENDPOINTS
# =============================================================================

@reports_bp.route('/export/excel/<report_type>')
def export_excel(report_type):
    """Excel export"""
    from services import export_to_excel
    from flask import send_file
    try:
        file_path = export_to_excel(report_type)
        return send_file(file_path, 
                        as_attachment=True,
                        download_name=f'{report_type}_report.xlsx',
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        from flask import flash, redirect, url_for
        flash(f'Excel export hatası: {str(e)}', 'error')
        return redirect(url_for('reports.index'))


@reports_bp.route('/export/pdf/<report_type>')
def export_pdf(report_type):
    """PDF export"""
    from services import export_to_pdf
    from flask import send_file
    try:
        file_path = export_to_pdf(report_type)
        return send_file(file_path,
                        as_attachment=True,
                        download_name=f'{report_type}_report.pdf',
                        mimetype='application/pdf')
    except Exception as e:
        from flask import flash, redirect, url_for
        flash(f'PDF export hatası: {str(e)}', 'error')
        return redirect(url_for('reports.index'))

@reports_bp.route('/invoice-report')
def invoice_report():
    """Fatura raporu"""
    db = DatabaseService()
    try:
        report = db.get_invoice_report()
        return render_template('reports/invoice_report.html', report=report)
    except Exception as e:
        print(f"Error loading invoice report: {e}")
        return render_template('reports/invoice_report.html', report=None)
    finally:
        db.close()

@reports_bp.route('/reading-success')
def reading_success():
    """Okuma başarı raporu"""
    db = DatabaseService()
    try:
        report = db.get_reading_success_report()
        return render_template('reports/reading_success.html', report=report)
    except Exception as e:
        print(f"Error loading reading success report: {e}")
        return render_template('reports/reading_success.html', report=None)
    finally:
        db.close()

@reports_bp.route('/loss-report')
def loss_report():
    """Kayıp/kaçak raporu - OSB kayıp analizi ile entegre"""
    db = DatabaseService()
    try:
        # OSB kayıp analiz fonksiyonunu kullan
        report = db.get_osb_loss_report()
        return render_template('reports/loss_report.html', report=report)
    except Exception as e:
        print(f"Error loading loss report: {e}")
        import traceback
        traceback.print_exc()
        return render_template('reports/loss_report.html', report=None)
    finally:
        db.close()

@reports_bp.route('/reactive-report')
def reactive_report():
    """Reaktif enerji raporu"""
    db = DatabaseService()
    try:
        report = db.get_reactive_report()
        return render_template('reports/reactive_report.html', report=report)
    except Exception as e:
        print(f"Error loading reactive report: {e}")
        return render_template('reports/reactive_report.html', report=None)
    finally:
        db.close()

# Demand report kaldırıldı - reactive_report içinde birleştirildi

@reports_bp.route('/comparison')
def comparison():
    """Karşılaştırma raporu"""
    db = DatabaseService()
    try:
        # Aylık tüketim karşılaştırması
        months = request.args.get('months', 12, type=int)
        
        db.cur.execute("""
            SELECT 
                TO_CHAR(reading_time, 'YYYY-MM') as period,
                SUM(total_consumption)::int as consumption,
                COUNT(DISTINCT meter_id) as meter_count,
                AVG(power_factor)::numeric(5,3) as avg_pf
            FROM readings
            WHERE reading_time >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '%s months')
            GROUP BY TO_CHAR(reading_time, 'YYYY-MM')
            ORDER BY period DESC
        """, (months,))
        data = [dict(row) for row in db.cur.fetchall()]
        
        # Chart data hazırla
        chart_data = {
            'labels': [r['period'] for r in data],
            'values': [r['consumption'] for r in data]
        }
        
        return render_template('reports/comparison.html', 
                             data=data,
                             chart_data=chart_data,
                             months=months)
    except Exception as e:
        print(f"Error loading comparison report: {e}")
        return render_template('reports/comparison.html', 
                             data=[],
                             chart_data=None,
                             months=12)
    finally:
        db.close()

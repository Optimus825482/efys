"""
EFYS Services Package
Tüm database fonksiyonlarını export eder
"""

# Core database service
from services.database import (
    DatabaseService,
    get_db,
    get_cursor,
    # Dashboard
    get_dashboard_stats,
    get_daily_consumption_chart,
    get_reactive_status,
    get_top_consumers,
    # Subscribers
    get_subscribers,
    get_subscriber_by_id,
    # Readings
    get_latest_readings,
    get_readings_by_meter,
    # Tariffs
    get_tariffs,
    get_tariff_by_id,
    # Billing
    get_billing_periods,
    calculate_invoice,
    # Monitoring
    get_meter_status_summary,
    get_hourly_consumption_profile,
)

# Extended database functions
from services.database_extensions import (
    # Billing Operations
    create_invoice,
    bulk_create_invoices,
    preview_invoice,
    cancel_invoice,
    add_additional_item,
    get_invoice_by_id,
    get_invoices_by_period,
    get_unpaid_invoices,
    # Reading Operations
    create_scheduled_reading,
    get_scheduled_readings,
    execute_scheduled_reading,
    retry_failed_reading,
    get_failed_readings,
    bulk_start_readings,
    # Subscriber Operations
    create_subscriber,
    update_subscriber,
    delete_subscriber,
    assign_meter_to_subscriber,
    get_subscriber_invoices,
    # Monitoring Operations
    get_missing_data,
    get_missing_data_stats,
    estimate_missing_data,
    get_alarms,
    create_alarm,
    acknowledge_alarm,
    # Export Operations
    export_to_excel,
    export_to_pdf,
)

__all__ = [
    # Core
    "DatabaseService",
    "get_db",
    "get_cursor",
    # Dashboard
    "get_dashboard_stats",
    "get_daily_consumption_chart",
    "get_reactive_status",
    "get_top_consumers",
    # Subscribers
    "get_subscribers",
    "get_subscriber_by_id",
    "create_subscriber",
    "update_subscriber",
    "delete_subscriber",
    "assign_meter_to_subscriber",
    "get_subscriber_invoices",
    # Readings
    "get_latest_readings",
    "get_readings_by_meter",
    "create_scheduled_reading",
    "get_scheduled_readings",
    "execute_scheduled_reading",
    "retry_failed_reading",
    "get_failed_readings",
    "bulk_start_readings",
    # Tariffs
    "get_tariffs",
    "get_tariff_by_id",
    # Billing
    "get_billing_periods",
    "calculate_invoice",
    "create_invoice",
    "bulk_create_invoices",
    "preview_invoice",
    "cancel_invoice",
    "add_additional_item",
    "get_invoice_by_id",
    "get_invoices_by_period",
    "get_unpaid_invoices",
    # Monitoring
    "get_meter_status_summary",
    "get_hourly_consumption_profile",
    "get_missing_data",
    "get_missing_data_stats",
    "estimate_missing_data",
    "get_alarms",
    "create_alarm",
    "acknowledge_alarm",
    # Export
    "export_to_excel",
    "export_to_pdf",
]

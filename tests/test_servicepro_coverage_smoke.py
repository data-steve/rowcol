def test_import_cash_reconciliation_module():
    from domains.ar.services import cash_reconciliation as cr  # noqa: F401
    assert hasattr(cr, "CashReconciliationService")


def test_import_data_ingestion_service():
    from domains.core.services.data_ingestion import DataIngestionService  # noqa: F401
    assert DataIngestionService is not None



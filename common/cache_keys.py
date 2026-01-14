class CacheKeys:
    @classmethod
    def pending_report_summary(cls, post_id: int):
        return f"pending-report-summary:post:{post_id}"

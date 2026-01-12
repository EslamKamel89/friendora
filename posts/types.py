from typing import TypedDict

from django.db.models import QuerySet

import posts.models as posts_models


class ReportSummaryInput(TypedDict):
    post_id: int
    post_author: str
    post_content: str
    post: posts_models.Post
    reports: QuerySet[posts_models.Report]

from .models import ActivityLog, Category, Decision, Project


def log_activity(user, action_type, description, decision=None, project=None):
    """
    Utility service for recording system audit events.
    """
    if not user or not user.is_authenticated:
        return None

    return ActivityLog.objects.create(
        user=user,
        action_type=action_type,
        description=description,
        decision=decision,
        project=project
    )


def get_dashboard_stats(user):
    """
    Computes dashboard analytics and summary metrics for the given user.
    """
    if not user or not user.is_authenticated:
        return {
            "total_projects": 0,
            "total_decisions": 0,
            "high_risk_decisions": 0,
            "pending_decisions": 0,
            "recent_activities": [],
            "recent_decisions": [],
            "risk_distribution": {}
        }

    user_projects = Project.objects.filter(owner=user)
    user_decisions = Decision.objects.filter(owner=user)

    total_projects = user_projects.count()
    total_decisions = user_decisions.count()
    high_risk_decisions = user_decisions.filter(risk_level__in=["HIGH", "CRITICAL"]).count()
    pending_decisions = user_decisions.filter(status__in=["DRAFT", "REVIEW"]).count()

    recent_activities = ActivityLog.objects.filter(user=user)[:8]
    recent_decisions = user_decisions.select_related("project", "category")[:5]

    risk_distribution = {
        "Low": user_decisions.filter(risk_level="LOW").count(),
        "Medium": user_decisions.filter(risk_level="MEDIUM").count(),
        "High": user_decisions.filter(risk_level="HIGH").count(),
        "Critical": user_decisions.filter(risk_level="CRITICAL").count(),
    }

    return {
        "total_projects": total_projects,
        "total_decisions": total_decisions,
        "high_risk_decisions": high_risk_decisions,
        "pending_decisions": pending_decisions,
        "recent_activities": recent_activities,
        "recent_decisions": recent_decisions,
        "risk_distribution": risk_distribution
    }


def seed_default_categories():
    """
    Ensures baseline decision categories exist in the system.
    """
    default_categories = [
        {"name": "Financial", "description": "Budget, investment, cost optimization, and revenue decisions.", "badge_color": "success", "icon_class": "bi-cash-coin"},
        {"name": "Technical", "description": "Architecture, software stack, infrastructure, and DevOps decisions.", "badge_color": "primary", "icon_class": "bi-cpu"},
        {"name": "Operational", "description": "Process improvements, workflow efficiency, and staffing decisions.", "badge_color": "warning", "icon_class": "bi-gear-wide-connected"},
        {"name": "Strategic", "description": "Long-term business goals, product vision, and market positioning.", "badge_color": "info", "icon_class": "bi-compass"},
        {"name": "Legal & Compliance", "description": "Regulatory requirements, privacy, GDPR, and contract decisions.", "badge_color": "danger", "icon_class": "bi-shield-check"},
        {"name": "Marketing & Sales", "description": "Campaign strategy, customer acquisition, and branding decisions.", "badge_color": "secondary", "icon_class": "bi-megaphone"},
    ]

    for cat in default_categories:
        Category.objects.get_or_create(
            name=cat["name"],
            defaults={
                "description": cat["description"],
                "badge_color": cat["badge_color"],
                "icon_class": cat["icon_class"]
            }
        )

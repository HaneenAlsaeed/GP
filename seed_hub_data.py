import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'final_project.settings')
django.setup()

from network.models import User
from decision_hub.models import Project, Category, Decision, Comment, ActivityLog, FavoriteDecision
from decision_hub.services import seed_default_categories, log_activity

def seed():
    print("Seeding AI Decision Hub baseline data...")
    seed_default_categories()

    # Get or create manager user
    manager, created = User.objects.get_or_create(username="manager_john")
    if created:
        manager.set_password("password123")
        manager.email = "john@enterprise.com"
        manager.save()

    print(f"Manager user: {manager.username}")

    # Create Projects
    p1, _ = Project.objects.get_or_create(
        title="Q3 Multi-Cloud Migration",
        owner=manager,
        defaults={"description": "Migration strategy and vendor evaluation for moving enterprise core workloads to AWS / Azure."}
    )

    p2, _ = Project.objects.get_or_create(
        title="AI Automation Pipeline",
        owner=manager,
        defaults={"description": "Implementation of LLM agents and workflow automation for customer service operations."}
    )

    p3, _ = Project.objects.get_or_create(
        title="GDPR & Data Security Audit",
        owner=manager,
        defaults={"description": "Regulatory compliance audit and database encryption upgrade for customer PII data."}
    )

    # Categories
    cat_tech = Category.objects.get(name="Technical")
    cat_fin = Category.objects.get(name="Financial")
    cat_op = Category.objects.get(name="Operational")
    cat_legal = Category.objects.get(name="Legal & Compliance")
    cat_strat = Category.objects.get(name="Strategic")

    # Decisions
    d1, _ = Decision.objects.get_or_create(
        title="Select Primary Cloud Infrastructure Provider (AWS vs Azure)",
        project=p1,
        owner=manager,
        defaults={
            "description": "Comprehensive evaluation of AWS EC2/EKS vs Azure Virtual Machines/AKS for workload migration. Includes 3-year TCO comparison, SLA guarantees, and compliance certifications.",
            "category": cat_tech,
            "risk_level": "HIGH",
            "priority": "URGENT",
            "status": "REVIEW",
            "impact_score": 85
        }
    )

    d2, _ = Decision.objects.get_or_create(
        title="Adopt Open-Source LLM (Llama 3) vs Proprietary API (OpenAI)",
        project=p2,
        owner=manager,
        defaults={
            "description": "Decision on hosting self-managed open-source models vs using third-party managed API endpoints. Evaluating data privacy, latency, and operational overhead.",
            "category": cat_tech,
            "risk_level": "MEDIUM",
            "priority": "HIGH",
            "status": "APPROVED",
            "impact_score": 75
        }
    )

    d3, _ = Decision.objects.get_or_create(
        title="Database Column Encryption for PII Compliance",
        project=p3,
        owner=manager,
        defaults={
            "description": "Implementation of AES-256 field-level encryption for user email and personal data to meet European Union GDPR requirements.",
            "category": cat_legal,
            "risk_level": "CRITICAL",
            "priority": "URGENT",
            "status": "IMPLEMENTED",
            "impact_score": 95
        }
    )

    d4, _ = Decision.objects.get_or_create(
        title="Vendor Contract Renewal with Datadog",
        project=p1,
        owner=manager,
        defaults={
            "description": "Negotiating 2-year enterprise commitment with Datadog for cloud observability and APM monitoring.",
            "category": cat_fin,
            "risk_level": "LOW",
            "priority": "MEDIUM",
            "status": "DRAFT",
            "impact_score": 40
        }
    )

    # Star favorite
    FavoriteDecision.objects.get_or_create(user=manager, decision=d1)
    FavoriteDecision.objects.get_or_create(user=manager, decision=d3)

    # Comments
    Comment.objects.get_or_create(
        decision=d1,
        author=manager,
        defaults={"text": "AWS offers better Kubernetes tooling (EKS), but Azure integrates seamlessly with our existing Active Directory."}
    )

    # Activity Logs
    log_activity(manager, "CREATE_PROJECT", f"Created project '{p1.title}'", project=p1)
    log_activity(manager, "CREATE_DECISION", f"Created decision '{d1.title}'", decision=d1, project=p1)
    log_activity(manager, "ADD_COMMENT", f"Commented on decision '{d1.title}'", decision=d1, project=p1)

    print("AI Decision Hub demo data successfully seeded!")

if __name__ == "__main__":
    seed()

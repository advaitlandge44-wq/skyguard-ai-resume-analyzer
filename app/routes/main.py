from flask import Blueprint, render_template, g, request
from app.models import Analysis, Resume
from app.services.security import login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Public landing page showcasing product features and ATS capabilities."""
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main user dashboard with performance stats and recent analyses."""
    user = g.user
    
    # User's analyses
    user_analyses = Analysis.query.filter_by(user_id=user.id).order_by(Analysis.created_at.desc())
    total_analyses = user_analyses.count()
    recent_analyses = user_analyses.limit(5).all()

    # Latest scores
    latest_analysis = recent_analyses[0] if recent_analyses else None
    
    # Calculate average scores across all analyses
    if total_analyses > 0:
        all_records = user_analyses.all()
        avg_resume_score = int(sum(a.overall_score for a in all_records) / total_analyses)
        avg_ats_score = int(sum(a.ats_score for a in all_records) / total_analyses)
        avg_match_score = int(sum(a.job_match_score for a in all_records) / total_analyses)
    else:
        avg_resume_score = 0
        avg_ats_score = 0
        avg_match_score = 0

    # Parsed data from latest analysis for skill profile badges
    latest_data = latest_analysis.parsed_data if latest_analysis else {}

    return render_template(
        'dashboard/dashboard.html',
        user=user,
        total_analyses=total_analyses,
        latest_analysis=latest_analysis,
        latest_data=latest_data,
        recent_analyses=recent_analyses,
        avg_resume_score=avg_resume_score,
        avg_ats_score=avg_ats_score,
        avg_match_score=avg_match_score
    )


@main_bp.route('/history')
@login_required
def history():
    """Full analysis history with search, filtering, and safe sorting."""
    user = g.user
    search_query = request.args.get('q', '').strip()
    query = Analysis.query.filter_by(user_id=user.id)
    if search_query:
        query = query.filter(Analysis.target_role.ilike(f"%{search_query}%"))

    # Whitelist-based safe sorting (Phase 19)
    allowed_sort_fields = {
        'date': Analysis.created_at.desc(),
        'score': Analysis.overall_score.desc(),
        'ats': Analysis.ats_score.desc(),
        'match': Analysis.job_match_score.desc()
    }
    sort_key = request.args.get('sort', 'date')
    order_clause = allowed_sort_fields.get(sort_key, Analysis.created_at.desc())

    analyses = query.order_by(order_clause).all()

    return render_template(
        'dashboard/history.html',
        analyses=analyses,
        search_query=search_query,
        current_sort=sort_key
    )


@main_bp.route('/my-resumes')
@login_required
def my_resumes():
    """List of all uploaded resume documents for the current user."""
    user = g.user
    resumes = Resume.query.filter_by(user_id=user.id).order_by(Resume.created_at.desc()).all()
    return render_template(
        'dashboard/my_resumes.html',
        resumes=resumes
    )


@main_bp.route('/roadmap')
@login_required
def roadmap():
    """Career roadmap view based on the latest resume analysis."""
    user = g.user
    latest_analysis = Analysis.query.filter_by(user_id=user.id).order_by(Analysis.created_at.desc()).first()
    data = latest_analysis.parsed_data if latest_analysis else {}
    
    return render_template(
        'dashboard/roadmap.html',
        analysis=latest_analysis,
        data=data
    )


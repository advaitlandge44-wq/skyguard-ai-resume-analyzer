from flask import Blueprint, render_template, redirect, url_for, flash, g, abort, request
from app.models import db, Analysis, ChatMessage
from app.services.security import login_required

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/results/<int:id>')
@login_required
def results(id: int):
    """Renders the comprehensive interactive results dashboard."""
    analysis = Analysis.query.get_or_404(id)
    
    # Ownership verification
    if analysis.user_id != g.user.id:
        abort(403)

    data = analysis.parsed_data
    chat_history = ChatMessage.query.filter_by(analysis_id=analysis.id).order_by(ChatMessage.created_at.asc()).all()

    return render_template(
        'analysis/results.html',
        analysis=analysis,
        data=data,
        chat_history=chat_history
    )


@analysis_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_analysis(id: int):
    """Deletes an analysis record and associated chat history."""
    analysis = Analysis.query.get_or_404(id)
    
    if analysis.user_id != g.user.id:
        abort(403)

    try:
        db.session.delete(analysis)
        db.session.commit()
        flash('Analysis record deleted successfully.', 'info')
    except Exception:
        db.session.rollback()
        flash('Failed to delete analysis record.', 'danger')

    return redirect(url_for('main.history'))


@analysis_bp.route('/export/<int:id>')
@login_required
def export_report(id: int):
    """Renders a clean, print-ready PDF/HTML report of the analysis."""
    analysis = Analysis.query.get_or_404(id)
    
    if analysis.user_id != g.user.id:
        abort(403)

    data = analysis.parsed_data
    return render_template(
        'analysis/export.html',
        analysis=analysis,
        data=data
    )

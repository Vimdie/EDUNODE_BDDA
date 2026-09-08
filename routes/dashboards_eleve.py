from flask import Blueprint, render_template, session, redirect, url_for, flash, Response, request
from models.queries import (
    get_student_info, get_student_notes, get_student_stats, get_student_ranking,
    get_teacher_info, get_teacher_courses, get_teacher_dashboard_stats, get_teacher_students_list,
    get_all_students, get_all_classes, get_all_filieres, get_admin_dashboard_stats,
    get_course_detail, get_course_evaluations, get_course_students_with_notes,
    get_class_ranking_by_course, get_class_note_distribution,
    create_evaluation, upsert_note, get_student_program, get_student_credits,
    update_student_profile_data
)

dashboards_bp = Blueprint('dashboards', __name__)

def role_required(role):
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                flash("Accès non autorisé.", "danger")
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        # Fix for blueprint endpoint name conflict
        wrapped_function.__name__ = f.__name__
        return wrapped_function
    return decorator

@dashboards_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    role = session.get('role')
    if role == 'etudiant':
        return redirect(url_for('dashboards.student_notes'))
    elif role == 'professeur':
        return redirect(url_for('dashboards.prof_courses'))
    elif role == 'admin':
        return redirect(url_for('dashboards.admin_students'))
    
    session.clear()
    return redirect(url_for('auth.login'))

@dashboards_bp.route('/student/notes')
@role_required('etudiant')
def student_notes():
    user_id = session['user_id']
    student_info = get_student_info(user_id)
    
    if not student_info:
        flash("Etudiant non trouvé.", "danger")
        return redirect(url_for('auth.logout'))
        
    notes = get_student_notes(student_info['id'])
    stats = get_student_stats(student_info['id'])
    ranking = get_student_ranking(student_info['id'])
    program = get_student_program(student_info['id'])
    credits_stats = get_student_credits(student_info['id'])
    
    return render_template(
        'dashboard_student.html', 
        student=student_info, 
        notes=notes, 
        stats=stats, 
        ranking=ranking,
        program=program,
        credits_stats=credits_stats
    )

@dashboards_bp.route('/student/update_profile', methods=['POST'])
@role_required('etudiant')
def update_student_profile():
    user_id = session['user_id']
    student_info = get_student_info(user_id)
    if not student_info:
        flash("Etudiant non trouvé.", "danger")
        return redirect(url_for('auth.logout'))
        
    nouveau_telephone = request.form.get('telephone')
    nouveau_sexe = request.form.get('sexe')
    nouvelle_date_naissance = request.form.get('date_naissance')
    nouvelle_nationalite = request.form.get('nationalite')
    
    if nouveau_telephone is not None:
        update_student_profile_data(
            student_info['id'], 
            nouveau_telephone, 
            nouveau_sexe, 
            nouvelle_date_naissance, 
            nouvelle_nationalite
        )
        flash("Profil mis à jour avec succès !", "success")
        
    return redirect(url_for('dashboards.student_notes') + '#profil')

@dashboards_bp.route('/prof/courses')
@role_required('professeur')
def prof_courses():
    user_id = session['user_id']
    prof_info = get_teacher_info(user_id)
    
    if not prof_info:
        flash("Professeur non trouvé.", "danger")
        return redirect(url_for('auth.logout'))
        
    courses = get_teacher_courses(prof_info['id'])
    stats = get_teacher_dashboard_stats(prof_info['id'])
    students = get_teacher_students_list(prof_info['id'])
    
    return render_template('dashboard_teacher.html', prof=prof_info, courses=courses, stats=stats, students=students)

@dashboards_bp.route('/admin/students')
@role_required('admin')
def admin_students():
    students = get_all_students()
    classes = get_all_classes()
    filieres = get_all_filieres()
    stats = get_admin_dashboard_stats()
    
    return render_template('dashboard_admin.html', students=students, classes=classes, filieres=filieres, stats=stats)

@dashboards_bp.route('/admin/export_students')
@role_required('admin')
def export_students():
    students = get_all_students()
    
    def generate():
        yield 'Matricule,Nom,Prenom,Sexe,Telephone\n'
        for s in students:
            yield f"{s['matricule']},{s['nom']},{s['prenom']},{s['sexe']},{s['telephone']}\n"
            
    return Response(
        generate(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=etudiants.csv'}
    )

# ──────── ROUTES PROFESSEUR AVANCÉES ────────

@dashboards_bp.route('/prof/course/<int:ens_id>')
@role_required('professeur')
def course_detail(ens_id):
    """Page détail d'un cours : étudiants, évaluations, classement, charts."""
    prof_info = get_teacher_info(session['user_id'])
    if not prof_info:
        flash("Professeur non trouvé.", "danger")
        return redirect(url_for('dashboards.prof_courses'))

    course = get_course_detail(ens_id)
    if not course:
        flash("Cours introuvable.", "danger")
        return redirect(url_for('dashboards.prof_courses'))

    evaluations = get_course_evaluations(ens_id)
    ranking = get_class_ranking_by_course(ens_id)
    distribution = get_class_note_distribution(ens_id)

    # Pour la saisie de notes, sélectionner l'évaluation active (première si disponible)
    selected_eval_id = request.args.get('eval_id', type=int)
    if not selected_eval_id and evaluations:
        selected_eval_id = evaluations[0]['id']

    students_with_notes = get_course_students_with_notes(ens_id, selected_eval_id)

    # Calcul de la moyenne de la classe pour ce cours
    notes_valides = [s['note'] for s in students_with_notes if s['note'] is not None]
    moyenne_classe = round(sum(notes_valides) / len(notes_valides), 2) if notes_valides else None

    return render_template('prof_course_detail.html',
        prof=prof_info,
        course=course,
        evaluations=evaluations,
        students=students_with_notes,
        ranking=ranking,
        distribution=distribution,
        selected_eval_id=selected_eval_id,
        moyenne_classe=moyenne_classe
    )

@dashboards_bp.route('/prof/course/<int:ens_id>/add_evaluation', methods=['POST'])
@role_required('professeur')
def add_evaluation(ens_id):
    """Crée une nouvelle évaluation pour un cours."""
    type_eval = request.form.get('type_eval', '').strip()
    try:
        coefficient = float(request.form.get('coefficient', 1))
    except ValueError:
        coefficient = 1.0
    date_eval = request.form.get('date_eval', '').strip()

    if not type_eval or not date_eval:
        flash("Veuillez remplir tous les champs de l'évaluation.", "warning")
    else:
        success = create_evaluation(ens_id, type_eval, coefficient, date_eval)
        if success:
            flash(f"Évaluation « {type_eval} » créée avec succès !", "success")
        else:
            flash("Erreur lors de la création de l'évaluation.", "danger")

    return redirect(url_for('dashboards.course_detail', ens_id=ens_id))

@dashboards_bp.route('/prof/evaluation/<int:eval_id>/saisie_notes', methods=['POST'])
@role_required('professeur')
def saisie_notes(eval_id):
    """Enregistre les notes saisies par le professeur pour une évaluation."""
    ens_id = request.form.get('ens_id', type=int)
    errors = 0
    saved = 0

    for key, val in request.form.items():
        if key.startswith('note_'):
            try:
                inscription_id = int(key.split('_')[1])
                if val.strip() == '':
                    continue
                note_val = float(val)
                if not 0 <= note_val <= 20:
                    errors += 1
                    continue
                valide = 'Oui' if note_val >= 10 else 'Non'
                ok = upsert_note(inscription_id, eval_id, note_val, valide)
                if ok:
                    saved += 1
                else:
                    errors += 1
            except (ValueError, IndexError):
                errors += 1

    if saved > 0:
        flash(f"{saved} note(s) enregistrée(s) avec succès !", "success")
    if errors > 0:
        flash(f"{errors} note(s) n'ont pas pu être enregistrées.", "warning")

    return redirect(url_for('dashboards.course_detail', ens_id=ens_id, eval_id=eval_id))

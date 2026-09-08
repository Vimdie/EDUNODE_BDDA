from flask import Blueprint, render_template, session, redirect, url_for, flash, Response, request
from models.queries import *

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
    
    return render_template('dashboard_student.html', student=student_info, notes=notes, stats=stats, ranking=ranking, program=program, credits_stats=credits_stats)

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
    teachers = get_all_teachers()
    classes = get_all_classes()
    filieres = get_all_filieres()
    stats = get_admin_dashboard_stats()
    
    return render_template('dashboard_admin.html', students=students, teachers=teachers, classes=classes, filieres=filieres, stats=stats)

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


@dashboards_bp.route('/student/update_profile', methods=['POST'])
@role_required('etudiant')
def update_student_profile():
    user_id = session['user_id']
    student_info = get_student_info(user_id)
    if not student_info:
        flash("Etudiant non trouv├®.", "danger")
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
        flash("Profil mis ├á jour avec succ├¿s !", "success")
        
    return redirect(url_for('dashboards.student_notes') + '#profil')

@dashboards_bp.route('/prof/course/<int:ens_id>')
@role_required('professeur')
def course_detail(ens_id):
    """Page d├®tail d'un cours : ├®tudiants, ├®valuations, classement, charts."""
    prof_info = get_teacher_info(session['user_id'])
    if not prof_info:
        flash("Professeur non trouv├®.", "danger")
        return redirect(url_for('dashboards.prof_courses'))

    course = get_course_detail(ens_id)
    if not course:
        flash("Cours introuvable.", "danger")
        return redirect(url_for('dashboards.prof_courses'))

    evaluations = get_course_evaluations(ens_id)
    ranking = get_class_ranking_by_course(ens_id)
    distribution = get_class_note_distribution(ens_id)

    # Pour la saisie de notes, s├®lectionner l'├®valuation active (premi├¿re si disponible)
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
    """Cr├®e une nouvelle ├®valuation pour un cours."""
    type_eval = request.form.get('type_eval', '').strip()
    try:
        coefficient = float(request.form.get('coefficient', 1))
    except ValueError:
        coefficient = 1.0
    date_eval = request.form.get('date_eval', '').strip()

    if not type_eval or not date_eval:
        flash("Veuillez remplir tous les champs de l'├®valuation.", "warning")
    else:
        success = create_evaluation(ens_id, type_eval, coefficient, date_eval)
        if success:
            flash(f"├ëvaluation ┬½ {type_eval} ┬╗ cr├®├®e avec succ├¿s !", "success")
        else:
            flash("Erreur lors de la cr├®ation de l'├®valuation.", "danger")

    return redirect(url_for('dashboards.course_detail', ens_id=ens_id))

@dashboards_bp.route('/prof/evaluation/<int:eval_id>/saisie_notes', methods=['POST'])
@role_required('professeur')
def saisie_notes(eval_id):
    """Enregistre les notes saisies par le professeur pour une ├®valuation."""
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
        flash(f"{saved} note(s) enregistr├®e(s) avec succ├¿s !", "success")
    if errors > 0:
        flash(f"{errors} note(s) n'ont pas pu ├¬tre enregistr├®es.", "warning")

    return redirect(url_for('dashboards.course_detail', ens_id=ens_id, eval_id=eval_id))

@dashboards_bp.route('/admin/add_student', methods=['POST'])
@role_required('admin')
def add_student():
    matricule = request.form.get('matricule')
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    sexe = request.form.get('sexe')
    date_naissance = request.form.get('date_naissance')
    telephone = request.form.get('telephone')
    nationalite = request.form.get('nationalite')
    boursier = request.form.get('boursier')
    email = request.form.get('email')
    password = request.form.get('password')

    if create_student_admin(matricule, nom, prenom, sexe, date_naissance, telephone, nationalite, boursier, email, password):
        flash("├ëtudiant cr├®├® avec succ├¿s !", "success")
    else:
        flash("Erreur lors de la cr├®ation de l'├®tudiant.", "danger")
    return redirect(url_for('dashboards.admin_students'))

@dashboards_bp.route('/admin/edit_student/<int:etudiant_id>', methods=['POST'])
@role_required('admin')
def edit_student(etudiant_id):
    matricule = request.form.get('matricule')
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    sexe = request.form.get('sexe')
    date_naissance = request.form.get('date_naissance')
    telephone = request.form.get('telephone')
    nationalite = request.form.get('nationalite')
    boursier = request.form.get('boursier')
    email = request.form.get('email')

    if update_student_admin(etudiant_id, matricule, nom, prenom, sexe, date_naissance, telephone, nationalite, boursier, email):
        flash("├ëtudiant mis ├á jour avec succ├¿s !", "success")
    else:
        flash("Erreur lors de la mise ├á jour de l'├®tudiant.", "danger")
    return redirect(url_for('dashboards.admin_students'))

@dashboards_bp.route('/admin/delete_student/<int:etudiant_id>', methods=['POST'])
@role_required('admin')
def delete_student(etudiant_id):
    if delete_student_admin(etudiant_id):
        flash("├ëtudiant supprim├® avec succ├¿s !", "success")
    else:
        flash("Erreur lors de la suppression de l'├®tudiant.", "danger")
    return redirect(url_for('dashboards.admin_students'))

@dashboards_bp.route('/admin/add_teacher', methods=['POST'])
@role_required('admin')
def add_teacher():
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    grade = request.form.get('grade')
    telephone = request.form.get('telephone')
    annee_embauche = request.form.get('annee_embauche')
    statut = request.form.get('statut')
    email = request.form.get('email')
    password = request.form.get('password')

    if create_teacher_admin(nom, prenom, grade, telephone, annee_embauche, statut, email, password):
        flash("Professeur cr├®├® avec succ├¿s !", "success")
    else:
        flash("Erreur lors de la cr├®ation du professeur.", "danger")
    return redirect(url_for('dashboards.admin_students'))

@dashboards_bp.route('/admin/edit_teacher/<int:prof_id>', methods=['POST'])
@role_required('admin')
def edit_teacher(prof_id):
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    grade = request.form.get('grade')
    telephone = request.form.get('telephone')
    annee_embauche = request.form.get('annee_embauche')
    statut = request.form.get('statut')
    email = request.form.get('email')

    if update_teacher_admin(prof_id, nom, prenom, grade, telephone, annee_embauche, statut, email):
        flash("Professeur mis ├á jour avec succ├¿s !", "success")
    else:
        flash("Erreur lors de la mise ├á jour du professeur.", "danger")
    return redirect(url_for('dashboards.admin_students'))

@dashboards_bp.route('/admin/delete_teacher/<int:prof_id>', methods=['POST'])
@role_required('admin')
def delete_teacher(prof_id):
    if delete_teacher_admin(prof_id):
        flash("Professeur supprim├® avec succ├¿s !", "success")
    else:
        flash("Erreur lors de la suppression du professeur.", "danger")
    return redirect(url_for('dashboards.admin_students'))
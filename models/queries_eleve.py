from database import get_db_connection

def authenticate_user(email, password):
    """Vérifie les informations de connexion."""
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute("SELECT idUtilisateur, Role FROM Utilisateur WHERE Email = ? AND MotDePasse = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    if user:
         return {"id": user[0], "role": user[1]}
    return None

def get_student_info(user_id):
    """Récupère les infos complètes d'un étudiant (profil, classe, filière, etc.)."""
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor()
    query = """
        SELECT e.idEtudiant, e.Matricule, e.Nom, e.Prenom, e.Sexe, e.DateNaissance, 
               e.Nationalite, e.Telephone, e.Boursier, u.Email, 
               c.NomClasse, f.NomFiliere
        FROM Etudiant e
        JOIN Utilisateur u ON e.Utilisateur_idUtilisateur = u.idUtilisateur
        LEFT JOIN Inscription i ON e.idEtudiant = i.Etudiant_idEtudiant
        LEFT JOIN Classe c ON i.Classe_idClasse = c.idClasse
        LEFT JOIN Filiere f ON c.Filiere_idFiliere = f.idFiliere
        WHERE e.Utilisateur_idUtilisateur = ?
    """
    cursor.execute(query, (user_id,))
    student = cursor.fetchone()
    conn.close()
    if student:
        return {
            "id": student[0], "matricule": student[1], "nom": student[2], 
            "prenom": student[3], "sexe": student[4], "date_naissance": student[5],
            "nationalite": student[6], "telephone": student[7], 
            "boursier": student[8], "email": student[9], 
            "classe": student[10], "filiere": student[11]
        }
    return None

def get_student_notes(etudiant_id):
    """Récupère les notes d'un étudiant."""
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor()
    query = """
        SELECT m.NomMatiere, e.TypeEvaluation, n.Note, n.Valide 
        FROM Note n
        JOIN Inscription i ON n.Inscription_idInscription = i.idInscription
        JOIN Evaluation e ON n.Evaluation_idEvaluation = e.idEvaluation
        JOIN Enseignement ens ON e.Enseignement_idEnseignement = ens.idEnseignement
        JOIN Programme p ON ens.Programme_idProgramme = p.idProgramme
        JOIN Matiere m ON p.Matiere_idMatiere = m.idMatiere
        WHERE i.Etudiant_idEtudiant = ?
    """
    cursor.execute(query, (etudiant_id,))
    notes = cursor.fetchall()
    conn.close()
    return [{"matiere": row[0], "evaluation": row[1], "note": float(row[2]) if row[2] is not None else 0, "valide": row[3]} for row in notes]

def get_teacher_info(user_id):
    """Récupère les infos complètes d'un professeur."""
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor()
    query = """
        SELECT p.idProfesseur, p.NomProfesseur, p.PrenomProfesseur, p.GradeSpecialite,
               p.Telephone, p.AnneeEmbauche, p.Statu, u.Email
        FROM Professeur p
        JOIN Utilisateur u ON p.Utilisateur_idUtilisateur = u.idUtilisateur
        WHERE p.Utilisateur_idUtilisateur = ?
    """
    cursor.execute(query, (user_id,))
    prof = cursor.fetchone()
    conn.close()
    if prof:
        return {
            "id": prof[0],
            "nom": prof[1],
            "prenom": prof[2],
            "grade": prof[3],
            "telephone": prof[4],
            "annee_embauche": prof[5],
            "statut": prof[6],
            "email": prof[7]
        }
    return None

def get_teacher_courses(prof_id):
    """Récupère les cours qu'un professeur enseigne (avec IDs pour la navigation)."""
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor()
    query = """
        SELECT ens.idEnseignement, m.NomMatiere, c.NomClasse, p.Semestre, m.Description,
               c.idClasse, ens.ModeCours, p.VolumeHoraire, p.Credit
        FROM Enseignement ens
        JOIN Programme p ON ens.Programme_idProgramme = p.idProgramme
        JOIN Matiere m ON p.Matiere_idMatiere = m.idMatiere
        JOIN Classe c ON p.Classe_idClasse = c.idClasse
        WHERE ens.Professeur_idProfesseur = ?
    """
    cursor.execute(query, (prof_id,))
    courses = cursor.fetchall()
    conn.close()
    return [{
        "id": row[0], "matiere": row[1], "classe": row[2], "semestre": row[3],
        "description": row[4], "classe_id": row[5], "mode_cours": row[6],
        "volume_horaire": row[7], "credit": float(row[8]) if row[8] else 0
    } for row in courses]

def get_all_students():
    """Récupère tous les étudiants (pour l'admin)."""
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor()
    query = "SELECT Matricule, Nom, Prenom, Sexe, Telephone FROM Etudiant"
    cursor.execute(query)
    students = cursor.fetchall()
    conn.close()
    return [{"matricule": row[0], "nom": row[1], "prenom": row[2], "sexe": row[3], "telephone": row[4]} for row in students]

def get_all_classes():
    """Récupère toutes les classes (pour l'admin)."""
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor()
    query = "SELECT c.NomClasse, f.NomFiliere FROM Classe c JOIN Filiere f ON c.Filiere_idFiliere = f.idFiliere"
    cursor.execute(query)
    classes = cursor.fetchall()
    conn.close()
    return [{"nom": row[0], "filiere": row[1]} for row in classes]

def get_all_filieres():
    """Récupère toutes les filières (pour l'admin)."""
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor()
    query = "SELECT NomFiliere, Description FROM Filiere"
    cursor.execute(query)
    filieres = cursor.fetchall()
    conn.close()
    return [{"nom": row[0], "description": row[1]} for row in filieres]

def get_student_program(etudiant_id):
    """
    Récupère le programme académique complet de l'étudiant 
    (matières, semestre, volume horaire, crédits, professeur).
    """
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor()
    query = """
        SELECT m.NomMatiere, p.Semestre, p.VolumeHoraire, p.Credit,
               prof.NomProfesseur, prof.PrenomProfesseur
        FROM Inscription i
        JOIN Programme p ON i.Classe_idClasse = p.Classe_idClasse 
                         AND i.AnneeAcademique_idAnneeacademique = p.AnneeAcademique_idAnneeacademique
        JOIN Matiere m ON p.Matiere_idMatiere = m.idMatiere
        LEFT JOIN Enseignement ens ON p.idProgramme = ens.Programme_idProgramme
        LEFT JOIN Professeur prof ON ens.Professeur_idProfesseur = prof.idProfesseur
        WHERE i.Etudiant_idEtudiant = ?
        ORDER BY p.Semestre, m.NomMatiere
    """
    cursor.execute(query, (etudiant_id,))
    program = cursor.fetchall()
    conn.close()
    
    return [{
        "matiere": row[0],
        "semestre": row[1],
        "volume_horaire": row[2],
        "credits": float(row[3]) if row[3] is not None else 0,
        "professeur": f"{row[5]} {row[4]}" if row[4] and row[5] else "Non assigné"
    } for row in program]

def get_student_credits(etudiant_id):
    """
    Calcule les crédits validés (notes >= 10 et statut 'Oui') vs les crédits totaux du programme.
    """
    conn = get_db_connection()
    if not conn: return {"valides": 0, "total": 0, "pourcentage": 0}
    cursor = conn.cursor()
    
    # Récupérer le total des crédits du programme de l'étudiant
    total_query = """
        SELECT SUM(p.Credit)
        FROM Inscription i
        JOIN Programme p ON i.Classe_idClasse = p.Classe_idClasse 
                         AND i.AnneeAcademique_idAnneeacademique = p.AnneeAcademique_idAnneeacademique
        WHERE i.Etudiant_idEtudiant = ?
    """
    cursor.execute(total_query, (etudiant_id,))
    total_row = cursor.fetchone()
    total_credits = float(total_row[0]) if total_row and total_row[0] is not None else 0
    
    # Récupérer les crédits validés
    valides_query = """
        SELECT SUM(p.Credit)
        FROM Note n
        JOIN Inscription i ON n.Inscription_idInscription = i.idInscription
        JOIN Evaluation e ON n.Evaluation_idEvaluation = e.idEvaluation
        JOIN Enseignement ens ON e.Enseignement_idEnseignement = ens.idEnseignement
        JOIN Programme p ON ens.Programme_idProgramme = p.idProgramme
        WHERE i.Etudiant_idEtudiant = ?
          AND n.Note >= 10
          AND n.Valide = 'Oui'
    """
    cursor.execute(valides_query, (etudiant_id,))
    valides_row = cursor.fetchone()
    credits_valides = float(valides_row[0]) if valides_row and valides_row[0] is not None else 0
    
    pourcentage = round((credits_valides / total_credits * 100)) if total_credits > 0 else 0
    
    conn.close()
    return {
        "valides": credits_valides,
        "total": total_credits,
        "pourcentage": pourcentage
    }

def update_student_profile_data(etudiant_id, telephone, sexe, date_naissance, nationalite):
    """Met à jour les informations de base de l'étudiant."""
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    query = """
        UPDATE Etudiant 
        SET Telephone = ?, Sexe = ?, DateNaissance = ?, Nationalite = ?
        WHERE idEtudiant = ?
    """
    cursor.execute(query, (telephone, sexe, date_naissance, nationalite, etudiant_id))
    conn.commit()
    conn.close()
    return True

def get_student_stats(etudiant_id):
    """Calcule la moyenne, et trouve la matière forte/faible."""
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor()
    query = """
        SELECT m.NomMatiere, n.Note, e.Coefficient
        FROM Note n
        JOIN Inscription i ON n.Inscription_idInscription = i.idInscription
        JOIN Evaluation e ON n.Evaluation_idEvaluation = e.idEvaluation
        JOIN Enseignement ens ON e.Enseignement_idEnseignement = ens.idEnseignement
        JOIN Programme p ON ens.Programme_idProgramme = p.idProgramme
        JOIN Matiere m ON p.Matiere_idMatiere = m.idMatiere
        WHERE i.Etudiant_idEtudiant = ? AND n.Note IS NOT NULL
    """
    cursor.execute(query, (etudiant_id,))
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        return {"moyenne": 0, "forte": "-", "faible": "-", "details_matieres": {}}
        
    total_points = 0
    total_coefs = 0
    matieres = {}
    
    for row in results:
        matiere = row[0]
        note = float(row[1])
        coef = float(row[2])
        
        total_points += (note * coef)
        total_coefs += coef
        
        if matiere not in matieres:
            matieres[matiere] = {"total": 0, "coef": 0}
        matieres[matiere]["total"] += (note * coef)
        matieres[matiere]["coef"] += coef
        
    moyenne_generale = float(round(total_points / total_coefs, 2)) if total_coefs > 0 else 0.0
    moyennes_matieres = {m: float(round(data["total"] / data["coef"], 2)) for m, data in matieres.items() if data["coef"] > 0}
    
    matiere_forte = max(moyennes_matieres.keys(), key=lambda k: moyennes_matieres[k]) if moyennes_matieres else "-"
    matiere_faible = min(moyennes_matieres.keys(), key=lambda k: moyennes_matieres[k]) if moyennes_matieres else "-"
    
    return {
        "moyenne": moyenne_generale,
        "forte": f"{matiere_forte} ({moyennes_matieres.get(matiere_forte, '')})",
        "faible": f"{matiere_faible} ({moyennes_matieres.get(matiere_faible, '')})",
        "details_matieres": moyennes_matieres
    }

def get_admin_dashboard_stats():
    """Récupère les statistiques globales pour l'administrateur."""
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor()
    stats = {}
    
    cursor.execute("SELECT COUNT(*) FROM Etudiant")
    stats['total_etudiants'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Professeur")
    stats['total_profs'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Classe")
    stats['total_classes'] = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT f.NomFiliere, COUNT(e.idEtudiant) 
        FROM Filiere f 
        LEFT JOIN Classe c ON f.idFiliere = c.Filiere_idFiliere 
        LEFT JOIN Inscription i ON c.idClasse = i.Classe_idClasse 
        LEFT JOIN Etudiant e ON i.Etudiant_idEtudiant = e.idEtudiant 
        GROUP BY f.NomFiliere
    """)
    stats['repartition_filiere'] = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    return stats

def get_teacher_dashboard_stats(prof_id):
    """Récupère les statistiques pour le dashboard professeur."""
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor()
    stats = {}
    
    cursor.execute("SELECT COUNT(DISTINCT Programme_idProgramme) FROM Enseignement WHERE Professeur_idProfesseur = ?", (prof_id,))
    stats['total_cours'] = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(DISTINCT i.Etudiant_idEtudiant) 
        FROM Enseignement ens
        JOIN Programme p ON ens.Programme_idProgramme = p.idProgramme
        JOIN Inscription i ON p.Classe_idClasse = i.Classe_idClasse
        WHERE ens.Professeur_idProfesseur = ?
    """, (prof_id,))
    stats['total_eleves'] = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT AVG(n.Note)
        FROM Note n
        JOIN Evaluation e ON n.Evaluation_idEvaluation = e.idEvaluation
        JOIN Enseignement ens ON e.Enseignement_idEnseignement = ens.idEnseignement
        WHERE ens.Professeur_idProfesseur = ? AND n.Note IS NOT NULL
    """, (prof_id,))
    avg = cursor.fetchone()[0]
    stats['moyenne_globale'] = float(round(float(avg), 2)) if avg is not None else 0.0
    
    conn.close()
    return stats

def get_teacher_students_list(prof_id):
    """Récupère la liste des étudiants enseignés par le professeur."""
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor()
    query = """
        SELECT DISTINCT e.Matricule, e.Nom, e.Prenom, c.NomClasse, m.NomMatiere
        FROM Etudiant e
        JOIN Inscription i ON e.idEtudiant = i.Etudiant_idEtudiant
        JOIN Classe c ON i.Classe_idClasse = c.idClasse
        JOIN Programme p ON c.idClasse = p.Classe_idClasse
        JOIN Matiere m ON p.Matiere_idMatiere = m.idMatiere
        JOIN Enseignement ens ON p.idProgramme = ens.Programme_idProgramme
        WHERE ens.Professeur_idProfesseur = ?
        ORDER BY c.NomClasse, e.Nom
    """
    cursor.execute(query, (prof_id,))
    students = cursor.fetchall()
    conn.close()
    return [{"matricule": row[0], "nom": row[1], "prenom": row[2], "classe": row[3], "matiere": row[4]} for row in students]

def get_student_ranking(etudiant_id):
    """Calcule le classement de l'étudiant dans sa classe."""
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor()
    
    # Trouver l'ID de la classe
    cursor.execute("""
        SELECT c.idClasse
        FROM Inscription i
        JOIN Classe c ON i.Classe_idClasse = c.idClasse
        WHERE i.Etudiant_idEtudiant = ?
    """, (etudiant_id,))
    res = cursor.fetchone()
    if not res:
        conn.close()
        return None
    classe_id = res[0]
    
    # Récupérer toutes les notes des élèves de cette classe
    cursor.execute("""
        SELECT i.Etudiant_idEtudiant, n.Note, e.Coefficient
        FROM Note n
        JOIN Inscription i ON n.Inscription_idInscription = i.idInscription
        JOIN Evaluation e ON n.Evaluation_idEvaluation = e.idEvaluation
        WHERE i.Classe_idClasse = ? AND n.Note IS NOT NULL
    """, (classe_id,))
    results = cursor.fetchall()
    conn.close()
    
    etu_stats = {}
    for row in results:
        etu = row[0]
        note = float(row[1])
        coef = float(row[2])
        if etu not in etu_stats:
            etu_stats[etu] = {"pts": 0.0, "coef": 0.0}
        etu_stats[etu]["pts"] += note * coef
        etu_stats[etu]["coef"] += coef
        
    averages = []
    for etu, data in etu_stats.items():
        avg = data["pts"] / data["coef"] if data["coef"] > 0 else 0
        averages.append((etu, avg))
        
    averages.sort(key=lambda x: x[1], reverse=True)
    
    rank = 0
    total = len(averages)
    for i, (etu, avg) in enumerate(averages):
        if etu == etudiant_id:
            rank = i + 1
            break
            
    return {"rang": rank, "total": total}

# ──────────────────────────────────────────────────────────────────────────────
# NOUVELLES FONCTIONS – ESPACE PROFESSEUR AVANCÉ
# ──────────────────────────────────────────────────────────────────────────────

def get_course_detail(ens_id):
    """Retourne les détails complets d'un Enseignement (cours)."""
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ens.idEnseignement, m.NomMatiere, m.Description, c.NomClasse,
               p.Semestre, p.VolumeHoraire, p.Credit, ens.ModeCours,
               f.NomFiliere, a.Libelle
        FROM Enseignement ens
        JOIN Programme p ON ens.Programme_idProgramme = p.idProgramme
        JOIN Matiere m ON p.Matiere_idMatiere = m.idMatiere
        JOIN Classe c ON p.Classe_idClasse = c.idClasse
        JOIN Filiere f ON c.Filiere_idFiliere = f.idFiliere
        JOIN AnneeAcademique a ON p.AnneeAcademique_idAnneeacademique = a.idAnneeacademique
        WHERE ens.idEnseignement = ?
    """, (ens_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0], "matiere": row[1], "description": row[2],
            "classe": row[3], "semestre": row[4], "volume_horaire": row[5],
            "credit": float(row[6]) if row[6] else 0, "mode_cours": row[7],
            "filiere": row[8], "annee": row[9]
        }
    return None

def get_course_evaluations(ens_id):
    """Retourne toutes les évaluations pour un Enseignement donné."""
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT idEvaluation, TypeEvaluation, Coefficient, DateEvaluation
        FROM Evaluation
        WHERE Enseignement_idEnseignement = ?
        ORDER BY DateEvaluation DESC
    """, (ens_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "type": r[1], "coefficient": float(r[2]), "date": r[3]} for r in rows]

def get_course_students_with_notes(ens_id, eval_id=None):
    """
    Retourne la liste des étudiants inscrits dans la classe du cours,
    avec leur note pour une évaluation donnée (ou None si pas encore saisie).
    """
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor()
    # Trouver la classe liée à cet enseignement
    cursor.execute("""
        SELECT p.Classe_idClasse FROM Enseignement ens
        JOIN Programme p ON ens.Programme_idProgramme = p.idProgramme
        WHERE ens.idEnseignement = ?
    """, (ens_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return []
    classe_id = row[0]

    cursor.execute("""
        SELECT e.idEtudiant, e.Matricule, e.Nom, e.Prenom, i.idInscription,
               n.idNote, n.Note, n.Valide, n.Session
        FROM Etudiant e
        JOIN Inscription i ON e.idEtudiant = i.Etudiant_idEtudiant
        LEFT JOIN Note n ON i.idInscription = n.Inscription_idInscription
                        AND n.Evaluation_idEvaluation = ?
        WHERE i.Classe_idClasse = ?
        ORDER BY e.Nom, e.Prenom
    """, (eval_id, classe_id))
    rows = cursor.fetchall()
    conn.close()
    return [{
        "etudiant_id": r[0], "matricule": r[1], "nom": r[2], "prenom": r[3],
        "inscription_id": r[4], "note_id": r[5],
        "note": float(r[6]) if r[6] is not None else None,
        "valide": r[7], "session": r[8]
    } for r in rows]

def get_class_ranking_by_course(ens_id):
    """
    Calcule le classement des étudiants de la classe
    basé sur la moyenne de toutes leurs notes dans ce cours.
    """
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.Nom, e.Prenom, e.Matricule,
               AVG(n.Note) as Moyenne,
               COUNT(n.idNote) as NbNotes
        FROM Etudiant e
        JOIN Inscription i ON e.idEtudiant = i.Etudiant_idEtudiant
        JOIN Note n ON i.idInscription = n.Inscription_idInscription
        JOIN Evaluation ev ON n.Evaluation_idEvaluation = ev.idEvaluation
        WHERE ev.Enseignement_idEnseignement = ? AND n.Note IS NOT NULL
        GROUP BY e.idEtudiant, e.Nom, e.Prenom, e.Matricule
        ORDER BY Moyenne DESC
    """, (ens_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{
        "nom": r[0], "prenom": r[1], "matricule": r[2],
        "moyenne": float(round(float(r[3]), 2)) if r[3] else 0,
        "nb_notes": r[4],
        "rang": i + 1
    } for i, r in enumerate(rows)]

def get_class_note_distribution(ens_id):
    """Retourne la répartition des notes par plage pour Chart.js."""
    conn = get_db_connection()
    if not conn: return {}
    cursor = conn.cursor()
    cursor.execute("""
        SELECT n.Note FROM Note n
        JOIN Evaluation ev ON n.Evaluation_idEvaluation = ev.idEvaluation
        WHERE ev.Enseignement_idEnseignement = ? AND n.Note IS NOT NULL
    """, (ens_id,))
    rows = cursor.fetchall()
    conn.close()
    distribution = {"0-5": 0, "5-10": 0, "10-15": 0, "15-20": 0}
    for r in rows:
        note = float(r[0])
        if note < 5: distribution["0-5"] += 1
        elif note < 10: distribution["5-10"] += 1
        elif note < 15: distribution["10-15"] += 1
        else: distribution["15-20"] += 1
    return distribution

def create_evaluation(ens_id, type_eval, coefficient, date_eval):
    """Insère une nouvelle évaluation dans la table Evaluation."""
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Evaluation (Enseignement_idEnseignement, TypeEvaluation, Coefficient, DateEvaluation)
            VALUES (?, ?, ?, ?)
        """, (ens_id, type_eval, coefficient, date_eval))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur create_evaluation: {e}")
        return False
    finally:
        conn.close()

def upsert_note(inscription_id, eval_id, note_val, valide='oui', session='Normale'):
    """
    Insère ou met à jour une note.
    Si elle existe (même inscription + evaluation), UPDATE.
    Sinon, INSERT.
    """
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT idNote FROM Note
            WHERE Inscription_idInscription = ? AND Evaluation_idEvaluation = ?
        """, (inscription_id, eval_id))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE Note SET Note = ?, Valide = ?, Session = ?
                WHERE idNote = ?
            """, (note_val, valide, session, existing[0]))
        else:
            cursor.execute("""
                INSERT INTO Note (Inscription_idInscription, Evaluation_idEvaluation, Note, Valide, Session)
                VALUES (?, ?, ?, ?, ?)
            """, (inscription_id, eval_id, note_val, valide, session))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur upsert_note: {e}")
        return False
    finally:
        conn.close()

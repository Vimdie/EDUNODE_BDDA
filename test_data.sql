-- Insertion des utilisateurs (Mot de passe: 1234, à hacher en sys reel)
INSERT INTO Utilisateur (Email, MotDePasse, Role) VALUES
('etudiant1@ecole.com', '1234', 'etudiant'),
('etudiant2@ecole.com', '1234', 'etudiant'),
('professeur1@ecole.com', '1234', 'professeur'),
('admin1@ecole.com', '1234', 'admin');
GO

-- Insertion d'une filière
INSERT INTO Filiere (NomFiliere, Description) VALUES
('Informatique', 'Développement Logiciel');
GO

-- Insertion d'une classe
INSERT INTO Classe (Filiere_idFiliere, NomClasse) VALUES
(1, 'L3 Info');
GO

-- Insertion de l'administrateur
INSERT INTO Administrateur (Filiere_idFiliere, Utilisateur_idUtilisateur, Nom, Prenom, Telephone, TypeAdmin) VALUES
(1, 4, 'Durand', 'Paul', '0600000000', 'Scolarite');
GO

-- Insertion des étudiants
INSERT INTO Etudiant (Utilisateur_idUtilisateur, Matricule, Nom, Prenom, Sexe, DateNaissance, Nationalite, Telephone, Boursier) VALUES
(1, 'ETU2024001', 'Martin', 'Alice', 'F', '2000-05-14', 'Française', '0611111111', 0),
(2, 'ETU2024002', 'Bernard', 'Lucas', 'M', '2001-08-22', 'Française', '0622222222', 1);
GO

-- Insertion du professeur
INSERT INTO Professeur (Utilisateur_idUtilisateur, NomProfesseur, PrenomProfesseur, Telephone, GradeSpecialite, AnneeEmbauche, Statu) VALUES
(3, 'Dupont', 'Jean', '0633333333', 'Docteur', 2015, 'Titulaire');
GO

-- Insertion d'une annee academique
INSERT INTO AnneeAcademique (Libelle, DateDebut, DateFin) VALUES
('2023-2024', '2023-09-01', '2024-06-30');
GO

-- Inscription des étudiants etudiants 1 et 2 dans L3 Info
INSERT INTO Inscription (AnneeAcademique_idAnneeacademique, Classe_idClasse, Etudiant_idEtudiant, Redoublant) VALUES
(1, 1, 1, 0),
(1, 1, 2, 0);
GO

-- Matières
INSERT INTO Matiere (NomMatiere, Description) VALUES
('Bases de données', 'Modélisation, SQL, NoSQL'),
('Programmation Web', 'HTML, CSS, JS, Python Flask');
GO

-- Programme
INSERT INTO Programme (Classe_idClasse, Matiere_idMatiere, AnneeAcademique_idAnneeacademique, Semestre, VolumeHoraire, Credit) VALUES
(1, 1, 1, 'S5', 60, 6.0),
(1, 2, 1, 'S5', 60, 6.0);
GO

-- Enseignement : le professeur Dupont enseigne les BDD et le dev web
INSERT INTO Enseignement (Programme_idProgramme, Professeur_idProfesseur, ModeCours) VALUES
(1, 1, 'Présentiel'),
(2, 1, 'Présentiel');
GO

-- Evaluation pour BDD
INSERT INTO Evaluation (Enseignement_idEnseignement, TypeEvaluation, Coefficient, DateEvaluation) VALUES
(1, 'Examen Final', 1.00, '2024-01-15');
GO

-- Notes 
-- Etudiant 1 a eu 15, Etudiant 2 a eu 12
-- Inscription ID = 1 pour etu 1, ID = 2 pour etu 2
-- Evaluation ID = 1
INSERT INTO Note (Inscription_idInscription, Evaluation_idEvaluation, Note, Valide, Session) VALUES
(1, 1, 15.00, 'Oui', 'Normale'),
(2, 1, 12.00, 'Oui', 'Normale');
GO

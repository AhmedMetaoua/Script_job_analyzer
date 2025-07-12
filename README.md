# Analyseur de Performance des Tâches

Un outil en ligne de commande Python qui analyse les données de performance des tâches depuis une base de données MySQL et génère des rapports PDF complets avec visualisations. L'outil envoie automatiquement les rapports par email et fournit des métriques détaillées de performance pour les tâches planifiées.

## Fonctionnalités

- 📊 **Analyse de Performance** : Analyse les temps d'exécution et les modèles des tâches
- 📈 **Rapports Visuels** : Génère des rapports PDF avec graphiques et analyses statistiques
- 📧 **Intégration Email** : Envoie automatiquement les rapports par email
- 🗄️ **Support Base de Données** : Se connecte aux bases de données MySQL via SQLAlchemy
- 📅 **Filtrage par Période** : Analyse des données pour des périodes spécifiques
- 🔧 **Configuration Flexible** : Arguments en ligne de commande pour personnalisation facile

## Prérequis

### Dépendances Python

```bash
pip install pandas matplotlib seaborn sqlalchemy pymysql
```

### Exigences Système

- Python 3.6+
- Base de données MySQL avec données de planification des tâches
- Compte Gmail pour l'envoi d'emails (ou configurer un autre SMTP)

## Installation

1. Clonez ou téléchargez le script
2. Installez les dépendances requises :
   ```bash
   pip install pandas matplotlib seaborn sqlalchemy pymysql
   ```
3. Configurez les paramètres email dans le script (voir section Configuration)

## Schéma de Base de Données

Le script s'attend à une table MySQL nommée `stg_scheduler_history` avec la structure suivante :

```sql
CREATE TABLE stg_scheduler_history (
    JOB_NAME VARCHAR(255),
    START_TIME DATETIME,
    END_TIME DATETIME
);
```

## Configuration

### Paramètres Email

Mettez à jour ces variables dans le script :

```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "votre-email@gmail.com"
EMAIL_PASSWORD = "votre-mot-de-passe-app"  # Utilisez un Mot de Passe d'App pour Gmail
```

**Note** : Pour Gmail, vous devez :

1. Activer l'authentification à 2 facteurs
2. Générer un Mot de Passe d'App
3. Utiliser le Mot de Passe d'App au lieu de votre mot de passe habituel

## Utilisation

### Utilisation Basique

```bash
python job_analyzer.py --email destinataire@example.com
```

### Utilisation Avancée

```bash
python job_analyzer.py \
    --email admin@entreprise.com \
    --host 192.168.1.100 \
    --user admin \
    --password secret \
    --database production_scheduler \
    --start-date 2025-01-01 \
    --end-date 2025-01-31 \
    --subject "Rapport de Performance Mensuel" \
    --save-pdf /chemin/vers/rapport.pdf \
    --verbose
```

## Arguments en Ligne de Commande

### Arguments Obligatoires

| Argument        | Description                           |
| --------------- | ------------------------------------- |
| `--email`, `-e` | Adresse email pour envoyer le rapport |

### Arguments de Connexion à la Base de Données

| Argument           | Défaut           | Description                     |
| ------------------ | ---------------- | ------------------------------- |
| `--host`           | `localhost`      | Hôte MySQL                      |
| `--user`, `-u`     | `root`           | Nom d'utilisateur MySQL         |
| `--password`, `-p` | `azerty`         | Mot de passe MySQL              |
| `--database`, `-d` | `scheduler_test` | Nom de la base de données MySQL |
| `--port`           | `3306`           | Port MySQL                      |

### Arguments de Période

| Argument       | Défaut       | Description                               |
| -------------- | ------------ | ----------------------------------------- |
| `--start-date` | `2025-05-01` | Date de début pour l'analyse (YYYY-MM-DD) |
| `--end-date`   | `2025-05-31` | Date de fin pour l'analyse (YYYY-MM-DD)   |

### Arguments Email

| Argument    | Défaut                                        | Description                |
| ----------- | --------------------------------------------- | -------------------------- |
| `--subject` | `Rapport d'Analyse de Performance des Tâches` | Sujet de l'email           |
| `--message` | Auto-généré                                   | Message email personnalisé |

### Arguments de Sortie

| Argument          | Description                              |
| ----------------- | ---------------------------------------- |
| `--save-pdf`      | Sauvegarder le PDF dans un fichier local |
| `--verbose`, `-v` | Activer la sortie détaillée              |

## Exemples

### Exemple 1 : Rapport Basique

```bash
python job_analyzer.py --email manager@entreprise.com
```

### Exemple 2 : Période Personnalisée

```bash
python job_analyzer.py \
    --email admin@entreprise.com \
    --start-date 2025-06-01 \
    --end-date 2025-06-30
```

### Exemple 3 : Base de Données Distante

```bash
python job_analyzer.py \
    --email admin@entreprise.com \
    --host db.entreprise.com \
    --user analytics \
    --password monmotdepasse \
    --database prod_scheduler
```

### Exemple 4 : Sauvegarde Locale

```bash
python job_analyzer.py \
    --email admin@entreprise.com \
    --save-pdf ./rapports/rapport_mensuel.pdf \
    --verbose
```

## Contenu du Rapport

Le rapport PDF généré inclut :

1. **Page de Résumé**

   - Total des tâches uniques
   - Total des exécutions de tâches
   - Moyenne des exécutions par tâche
   - Statistiques détaillées pour chaque tâche

2. **Graphiques de Performance**

   - Tendances de durée quotidienne pour chaque tâche
   - Lignes de durée moyenne, minimale et maximale
   - Analyse statistique

3. **Statistiques des Tâches**
   - Nombre d'exécutions
   - Durée moyenne
   - Plage de durée
   - Temps total passé

## Format de Sortie

### Sortie Console (Mode Verbose)

```
[2025-07-12 10:30:15] Analyseur de Performance des Tâches - Démarrage de l'analyse
[2025-07-12 10:30:15] Connexion à MySQL : localhost:3306/scheduler_test
[2025-07-12 10:30:16] Exécution de la requête SQL...
[2025-07-12 10:30:16] 1250 enregistrements récupérés de la base de données
[2025-07-12 10:30:16] Traitement des données de tâches...
[2025-07-12 10:30:16] Données filtrées : 890 enregistrements pour la période 2025-05-01 à 2025-05-31
[2025-07-12 10:30:16] Génération du rapport PDF : /tmp/job_analysis_xyz.pdf
[2025-07-12 10:30:18] Génération des graphiques pour 15 tâches...
[2025-07-12 10:30:22] Rapport PDF généré avec succès
[2025-07-12 10:30:22] Envoi de l'email à : admin@entreprise.com
[2025-07-12 10:30:25] Email envoyé avec succès !
[2025-07-12 10:30:25] Analyse de Performance des Tâches terminée avec succès !
```

## Dépannage

### Problèmes Courants

1. **Erreur de Connexion à la Base de Données**

   ```
   Erreur de connexion à la base de données : (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server")
   ```

   - Vérifiez l'hôte, le port, le nom d'utilisateur et le mot de passe
   - Assurez-vous que le serveur MySQL fonctionne
   - Vérifiez les paramètres du pare-feu

2. **Erreur d'Envoi d'Email**

   ```
   Échec de l'envoi d'email : (535, '5.7.8 Username and Password not accepted')
   ```

   - Utilisez un Mot de Passe d'App pour Gmail
   - Vérifiez les paramètres SMTP
   - Vérifiez les identifiants email

3. **Aucune Donnée Trouvée**

   ```
   Aucune donnée de tâche trouvée pour la période spécifiée
   ```

   - Vérifiez les paramètres de période
   - Vérifiez que les données existent dans la base de données
   - Vérifiez le nom de la table et des colonnes

4. **Erreur de Permission**
   ```
   Permission refusée : '/chemin/vers/rapport.pdf'
   ```
   - Vérifiez les permissions du chemin de fichier
   - Assurez-vous que le répertoire existe
   - Utilisez des chemins absolus

### Conseils de Débogage

1. Utilisez le flag `--verbose` pour une sortie détaillée
2. Testez la connexion à la base de données séparément
3. Vérifiez les identifiants email avec un test simple
4. Vérifiez les formats de date (YYYY-MM-DD)

## Licence

Ce script est fourni tel quel pour un usage éducatif et professionnel.

## Support

Pour les problèmes ou questions :

1. Consultez la section dépannage
2. Vérifiez votre configuration
3. Testez les composants individuels (base de données, email) séparément

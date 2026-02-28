"""Email generator service for administrative emails."""
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class EmailType(str, Enum):
    """Email types for administrative requests."""
    ATTESTATION = "attestation_inscription"
    ABSENCE = "justification_absence"
    STAGE = "demande_stage"
    RELEVE = "demande_releve_notes"
    RECLAMATION = "reclamation_note"


@dataclass
class EmailTemplate:
    """Email template definition."""
    label: str
    subject: str
    body: str
    fields: list


# Email templates registry
TEMPLATES = {
    EmailType.ATTESTATION: EmailTemplate(
        label="Demande d'attestation d'inscription",
        subject="Demande d'attestation d'inscription - {nom_prenom} - {filiere} {niveau}",
        body="""Madame, Monsieur,

Je soussigne(e) {nom_prenom}, etudiant(e) en {filiere} - Niveau {niveau} a l'Institut 
International de Technologie (IIT), numero de carte etudiant {numero_etudiant}, vous adresse 
la presente afin de solliciter la delivrance d'une attestation d'inscription pour l'annee 
academique {annee_academique}.

Ce document m'est necessaire pour {motif}.

Je reste a votre disposition pour tout renseignement complementaire et vous prie d'agreer, 
Madame, Monsieur, l'expression de mes salutations distinguees.

{nom_prenom}
Etudiant(e) IIT - {filiere} {niveau}
Contact : {email_etudiant}""",
        fields=["nom_prenom", "filiere", "niveau", "numero_etudiant", "annee_academique", "motif", "email_etudiant"],
    ),
    EmailType.ABSENCE: EmailTemplate(
        label="Justification d'absence",
        subject="Justification d'absence - {nom_prenom} - {date_absence}",
        body="""Madame, Monsieur,

Je soussigne(e) {nom_prenom}, etudiant(e) en {filiere} - Niveau {niveau} a l'IIT, me permets 
de porter a votre connaissance que j'ai ete dans l'impossibilite d'assister au(x) cours du 
{date_absence} en raison de {motif_absence}.

Veuillez trouver ci-joint les justificatifs correspondants.

Je vous prie de bien vouloir excuser cette absence et d'agreer, Madame, Monsieur, l'expression 
de mes salutations respectueuses.

{nom_prenom}
{filiere} - {niveau}""",
        fields=["nom_prenom", "filiere", "niveau", "date_absence", "motif_absence"],
    ),
    EmailType.STAGE: EmailTemplate(
        label="Demande de convention de stage",
        subject="Demande de convention de stage - {nom_prenom} - {entreprise}",
        body="""Madame, Monsieur,

Je soussigne(e) {nom_prenom}, etudiant(e) en {filiere} - {niveau} a l'Institut International 
de Technologie, vous sollicite afin d'obtenir une convention de stage dans le cadre de mon stage 
{type_stage} prevu du {date_debut} au {date_fin}.

L'entreprise d'accueil est : {entreprise}, sise a {adresse_entreprise}.
Le maitre de stage designe est : {maitre_stage}, {poste_maitre_stage}.

Je reste disponible pour tout complement d'information et vous remercie de l'attention portee 
a ma demande.

Cordialement,
{nom_prenom} | {filiere} {niveau} | IIT
Contact : {email_etudiant}""",
        fields=["nom_prenom", "filiere", "niveau", "type_stage", "date_debut", "date_fin", 
                "entreprise", "adresse_entreprise", "maitre_stage", "poste_maitre_stage", "email_etudiant"],
    ),
    EmailType.RELEVE: EmailTemplate(
        label="Demande de releve de notes",
        subject="Demande de releve de notes - {nom_prenom} - {semestre}",
        body="""Madame, Monsieur,

Je soussigne(e) {nom_prenom}, etudiant(e) en {filiere} - {niveau} 
(numero etudiant : {numero_etudiant}), souhaite obtenir mon releve de notes du {semestre} 
de l'annee academique {annee_academique}.

Ce document m'est necessaire pour {motif}.

Je vous remercie de bien vouloir traiter ma demande dans les meilleurs delais.

Cordialement,
{nom_prenom}""",
        fields=["nom_prenom", "filiere", "niveau", "numero_etudiant", "semestre", "annee_academique", "motif"],
    ),
    EmailType.RECLAMATION: EmailTemplate(
        label="Reclamation de note",
        subject="Reclamation de note - {module} - {nom_prenom}",
        body="""Madame, Monsieur,

Je soussigne(e) {nom_prenom}, etudiant(e) en {filiere} - {niveau}, me permets de formuler une 
reclamation concernant la note obtenue au module {module} lors de la session {session} de 
l'annee academique {annee_academique}.

Note obtenue : {note_obtenue}/20
Motif de la reclamation : {motif_reclamation}

Je solicite respectueusement un reexamen de ma copie ou un entretien avec l'enseignant concerne.

Dans l'attente de votre retour, je vous adresse mes salutations respectueuses.

{nom_prenom} - {numero_etudiant}""",
        fields=["nom_prenom", "filiere", "niveau", "module", "session", "annee_academique", 
                "note_obtenue", "motif_reclamation", "numero_etudiant"],
    ),
}


class EmailGenerator:
    """Email generator for administrative emails.
    
    Generates standardized administrative emails from templates.
    """

    def __init__(self, templates: dict = TEMPLATES) -> None:
        self._templates = templates

    def get_templates(self) -> list:
        """Get list of available templates."""
        return [
            {"type": t.value, "label": template.label, "fields": template.fields}
            for t, template in self._templates.items()
        ]

    def generate_email(self, context: str, template: str = None, **kwargs) -> str:
        """Generate an email based on context and optional template.
        
        Args:
            context: Context/information for the email
            template: Optional template type
            **kwargs: Template field values
            
        Returns:
            Generated email content
        """
        if template:
            try:
                email_type = EmailType(template)
                template_obj = self._templates[email_type]
                return template_obj.body.format(**kwargs) if kwargs else context
            except (ValueError, KeyError) as e:
                logger.warning(f"Template {template} not found: {e}")
        
        # Return context as plain email if no template
        return context

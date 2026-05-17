import streamlit as st
import re

# Configuration de la page en mode Large pour ton double écran
st.set_page_config(page_title="⚡ Dash'SDR", layout="wide")

st.title("⚡ Dash'SDR - Spécial DCE & Appels d'Offres")
st.caption("Outil de structuration de données CRM & Alignement de valeur instantané")

# =========================================================================
# CONTEXTE PRODUIT COMMERCIAL - KAYRO (FÉVRIER 2026)
# =========================================================================
KAYRO_OFFERS_CONTEXT = """
OFFRES ET MODULES DE L'IA KAYRO :

1. Traitement des Appels d'Offres (Réduction du temps de 3 jours à quelques heures) :
- Lecture DCE & synthèse RC/CCTP/annexes (jusqu'à 800 pages) en quelques minutes.
- Extraction automatique des délais, pénalités, clauses sensibles, pièces à fournir.
- Scoring Go/No-Go et qualification des AO selon critères internes, allocation des équipes.
- Génération de brouillons de mémoires techniques à partir du RC/CCTP et réutilisation des dossiers passés.
- Adaptation automatique au donneur d'ordre et à ses critères d'évaluation.
- Checklist de conformité : vérification du présent / manquant / à clarifier avant dépôt.
- Pré-remplissage des informations administratives récurrentes (réduction des oublis).
- Recherche sémantique dans l'historique des AO et des mémoires techniques passés.
- Pré-remplissage et harmonisation des libellés DPGF en cohérence avec l'AO.

2. Chiffrages & Consultation Fournisseurs :
- Comparaison assistée des offres de consultation fournisseurs et analyse automatique des écarts.
- Extraction automatique des devis (fin de la ressaisie manuelle, structuration automatique).
- Benchmark interne et alertes sur les dérives de coûts par rapport à l'historique des chantiers.

3. Suivi Opérationnel de Chantier :
- Génération de comptes-rendus structurés automatiques par chantier à partir de notes vocales + photos.
- Suivi et vérification de la conformité des sous-traitants (KBIS, attestations, alertes échéances, registre centralisé).
- Génération de documents de sécurité : PPSPS, analyses de risques, check-lists HSE.
- Détection des risques sur photos : rapprochement automatique avec l'analyse de risques et alertes de non-conformités.
- Synthèse hebdomadaire de l'avancement, des risques et des points bloquants par chantier.

4. Capitalisation & Fonctions Support :
- Base de connaissances : recherche intelligente dans les DTU, REX chantiers et procédures internes.
- Conformité produits : synthèse des avis techniques ATEX/CSTB et limites d'emploi.
- Veille réglementaire : synthèses juridiques automatisées et schémas de process.
- Automatisation administrative : génération de documents obligatoires, relances sous-traitants, mails récurrents.
- Tri des mails et routage des actions : priorisation et extraction des tâches chantier/AO.
- Synthèse Direction : tableau de bord mensuel en une page (alertes, avancements).
- Recrutement : qualification des CV, shortlists et questions d'entretien sur les métiers en tension.

RÉFÉRENCES ET ACTEURS ACCOMPAGNÉS :
- Bédier, SPECV (Secteur : Rénovation)
- G-ON, Sinteo (Secteur : Bureau d'études)
- Legrand (Secteur : Géomètres)
- FACE (Secteur : Bâtiments acier)
- Groupe Legendre, K entreprise (Secteur : Construction générale - En discussion)
"""

# Matrice des douleurs et des accroches par secteur
sdr_matrix = {
    "🧱 Gros Œuvre / BTP": {
        "pain": "Pénalités de retard explosives, clauses d'intempéries et gestion des sous-traitants cachées dans les annexes.",
        "hook": "« Sur vos gros chantiers, comment suivez-vous les pénalités masquées dans les 400 pages d'annexes ? »"
    },
    "⚡ Électricité / Fluides": {
        "pain": "Variantes techniques imposées, marques de matériel obligatoires dissimulées et limites de lots floues.",
        "hook": "« Comment traquez-vous les variantes de matériel imposées dans le CCTP sans y passer vos nuits ? »"
    },
    "📐 Bureau d'Études": {
        "pain": "Temps record perdu par les ingénieurs à décortiquer le RC juste pour qualifier le Go/No-Go technique.",
        "hook": "« Combien d'heures vos ingénieurs perdent-ils sur le RC juste pour savoir si vous êtes qualifiés ? »"
    },
    "🛠️ Second Œuvre": {
        "pain": "Plannings d'exécution ultra-serrés, responsabilité des interfaces et critères de conformité stricts.",
        "hook": "« Face aux plannings serrés du CCTP, comment sécurisez-vous vos limites de prestations ? »"
    }
}

# Fonction de nettoyage et de découpage automatique (Parser)
def parse_sdr_line(line):
    # 1. Extraction Email
    email_match = re.search(r'[\w.-]+@[\w.-]+\.[\w.-]+', line)
    email = email_match.group(0) if email_match else ""
    if email: line = line.replace(email, "")

    # 2. Extraction LinkedIn
    linkedin_match = re.search(r'https?://(www\.)?linkedin\.com/[^\s]+', line)
    linkedin = linkedin_match.group(0) if linkedin_match else ""
    if linkedin: line = line.replace(linkedin, "")

    # 3. Extraction Téléphone
    phone_match = re.search(r'(?:\+?33|0)[1-9](?:[\s.-]*\d{2}){4}|\b33\d{9}\b', line)
    phone = phone_match.group(0) if phone_match else ""
    if phone: line = line.replace(phone, "")

    # 4. Séparation Nom / Entreprise
    remaining = re.sub(r'\s+', ' ', line).strip()
    words = remaining.split(' ')
    
    if len(words) >= 2:
        prospect = f"{words[0]} {words[1]}"
        company = " ".join(words[2:]) if len(words) > 2 else "Entreprise Inconnue"
    else:
        prospect = "Non spécifié"
        company = remaining if remaining else "Entreprise Inconnue"
        
# 5. DICTIONNAIRE SÉMANTIQUE DE TRI AUTOMATIQUE (Mise à jour exhaustive Fr/En)
    lower_all = (company + " " + remaining).lower()
    
    # Mots-clés pour les Bureaux d'Études et l'Ingénierie (À checker en premier)
    keywords_bet = [
        'etude', 'inge', 'conseil', 'architecture', 'archi', 'bet', 'moe', "maitrise d'oeuvre", 
        'structure', 'economiste', 'acoustique', 'geometre', 'urbanisme', 'technique', 'solutions', 
        'civil engineering', 'engineering', 'genie civil', 'infra', 'superstructure', 'consulting', 
        'consultancy', 'architect', 'design office', 'cabinet', 'audit', 'expertise', 'amo', 'bureau d\'etudes'
    ]
    
    # Mots-clés pour l'Électricité, les Fluides et le Génie Climatique
    keywords_elec = [
        'elec', 'electricite', 'energie', 'fluide', 'spie', 'ineo', 'climatisation', 'cvc', 
        'chauffage', 'plomberie', 'thermique', 'cfa', 'cfo', 'courants forts', 'courants faibles', 
        'ventilation', 'solar', 'photovoltaique', 'sanitaire', 'genie climatique', 'engie', 
        'hvac', 'electricity', 'energy', 'electrical', 'plumbing', 'heating', 'lighting', 'cablage'
    ]
    
    # Mots-clés pour le Second Œuvre et les Finitions
    keywords_second = [
        'peinture', 'menuis', 'sol', 'platr', 'isolation', 'facade', 'etancheite', 'vitrerie', 
        'serrurerie', 'metallerie', 'agencement', 'platrerie', 'faux plafond', 'carrelage', 
        'renovation', 'finishing', 'interior', 'painting', 'drywall', 'insulation', 'tiling', 
        'flooring', 'carpentry', 'fit-out', 'revetement', 'placo', 'vitrage', 'amenagement'
    ]
    
    # Mots-clés spécifiques au Gros Œuvre / Travaux Publics / Entreprises Générales
    keywords_gros = [
        'maconnerie', 'terrassement', 'demolition', 'gros oeuvre', 'fondation', 'charpente', 
        'beton', 'tp', 'travaux publics', 'vinci', 'eiffage construction', 'bouygues construction', 
        'general contractor', 'masonry', 'concrete', 'excavation', 'infrastructure', 'btp', 
        'construction', 'batiment', 'contractor'
    ]
    
  # LOGIQUE DE TRI PAR PRIORITÉ (Avec les noms de clés d'origine pour éviter le bug)
    if any(x in lower_all for x in keywords_bet):
        sector = "📐 Bureau d'Études"
    elif any(x in lower_all for x in keywords_elec):
        sector = "⚡ Électricité / Fluides"
    elif any(x in lower_all for x in keywords_second):
        sector = "🛠️ Second Œuvre"
    else:
        sector = "🧱 Gros Œuvre / BTP"

    return {
        "prospect": prospect,
        "company": company,
        "email": email,
        "linkedin": linkedin,
        "phone": phone,
        "sector": sector
    }

# --- BARRE LATÉRALE : CONFIGURATION IA & DOCS ---
with st.sidebar:
    st.header("🔑 Configuration de l'Agent IA")
    gemini_key = st.text_input("Colle ta clé API Gemini (Gratuite) :", type="password")
    
    st.markdown("---")
    st.header("📄 Tes Cas d'Usages / Sales Deck")
    uploaded_docs = st.file_uploader(
        "Importe le doc de ta boîte (TXT ou PDF) pour guider l'IA :", 
        type=["txt", "pdf"], 
        accept_multiple_files=True
    )
    
    # Lecture simple du contenu des documents s'ils existent
    context_docs = ""
    if uploaded_docs:
        for doc in uploaded_docs:
            if doc.type == "text/plain":
                context_docs += "\n" + str(doc.read(), "utf-8")
            else:
                context_docs += f"\n[Document joint: {doc.name}]" # Extension PDF traitable via pypdf si besoin
        st.success("📚 Documents de contexte chargés !")

import google.generativeai as genai

def get_live_ai_pitch(company_name, sector, internal_context, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=[{"google_search": {}}]
        )
        
        full_context = KAYRO_OFFERS_CONTEXT
        if internal_context:
            full_context += "\n\nINFORMATIONS COMPLÉMENTAIRES JOINTES :\n" + internal_context
        
        prompt = f"""
        Tu es un SDR d'élite pour la solution d'IA Kayro dédiée au secteur de la construction.
        Ton but est de préparer un appel de prospection téléphonique ultra-personnalisé.
        
        ÉTAPES À SUIVRE :
        1. Fais une recherche Google en direct sur l'entreprise '{company_name}' (Secteur théorique : {sector}). Analyse leur site internet : quels types de projets ou chantiers précis réalisent-ils en ce moment ? Ont-ils des problématiques visibles (ex: marchés publics complexes, chantiers d'envergure, sous-traitance massive, ingénierie complexe, etc.) ?
        
        2. Analyse notre catalogue d'offres Kayro ci-dessous pour trouver le meilleur point d'ancrage :
        ---
        {{full_context}}
        ---
        
        3. Fais le lien ("Value Mapping") : Sélectionne l'offre ou le module spécifique de Kayro qui apportera le plus de valeur immédiate à cette entreprise compte tenu de ses vrais projets trouvés sur le web.
        
        CONSIGNES DE RÉDACTION (Sois percutant, pas de jargon générique) :
        - PAIN : Rédige une analyse de 2 à 3 phrases max. Identifie la douleur exacte qu'ils rencontrent sur leurs dossiers d'appels d'offres ou sur leurs chantiers. CITE UN EXEMPLE CONCRET ou un type de projet trouvé sur leur site pour prouver qu'on les connaît (ex: "Vu vos projets dans le domaine [X], la traque des pénalités de retard dans le CCTP doit vous prendre un temps fou...").
        - HOOK : Rédige une seule question d'accroche (Moins de 15 mots), directe et piquante, à poser dès le début du cold call pour capter leur attention sur ce module précis de Kayro.
        
        FORMAT DE RÉPONSE STRICT :
        PAIN: [Ton analyse]
        HOOK: [Ta question d'accroche]
        """
        
        response = model.generate_content(prompt)
        text = response.text
        
        pain = text.split("PAIN:")[1].split("HOOK:")[0].strip() if "PAIN:" in text else "Analyse indisponible."
        hook = text.split("HOOK:")[1].strip() if "HOOK:" in text else "Accroche indisponible."
        
        return { pain, hook
    except Exception as e:
        return f"Erreur IA : {str(e)}", "Veuillez vérifier la configuration."

    } 
        
# --- INTERFACE GRAPHIQUE ---

# Zone d'écriture des lignes CRM brutes
raw_input = st.text_area(
    "1. Colle ici ta ligne ou ta liste de prospects copiée d'Excel / CRM :", 
    height=120, 
    placeholder="Exemple :\nPhilippe Baudry Artea BTP 33609288487 philippe@arteia.com https://www.linkedin.com/in/philippe-baudry-5a1854a"
)

if raw_input:
    lines = [l.strip() for l in raw_input.split('\n') if l.strip()]
    
    if lines:
        st.markdown("---")
        st.subheader("🎯 Tes Fiches d'Appels Personnalisées")
        
        # Pour chaque ligne collée, on crée une "carte" visuelle claire
        for idx, current_line in enumerate(lines):
            data = parse_sdr_line(current_line)
            
            # Encadré propre pour chaque prospect
            with st.container(border=True):
                col_info, col_sector, col_pitch = st.columns([3, 3, 5])
                
                with col_info:
                    st.markdown(f"### 👤 {data['prospect']}")
                    st.markdown(f"**🏢 Entreprise :** `{data['company']}`")
                    
                    # Liens et contacts cliquables
                    contacts = []
                    if data['phone']: contacts.append(f"📞 **{data['phone']}**")
                    if data['email']: contacts.append(f"✉️ [Mail](mailto:{data['email']})")
                    if data['linkedin']: contacts.append(f"🔗 [LinkedIn]({data['linkedin']})")
                    
                    if contacts:
                        st.markdown(" | ".join(contacts))
                    else:
                        st.caption("Aucune coordonnée détectée")
                
                with col_sector:
                    # Menu déroulant pour ajuster le secteur manuellement si l'auto-détection s'est trompée
                    selected_sector = st.selectbox(
                        f"Ajuster le secteur de {data['company']}", 
                        list(sdr_matrix.keys()), 
                        index=list(sdr_matrix.keys()).index(data['sector']),
                        key=f"select_{idx}"
                    )
                
                with col_pitch:
                    # Affichage dynamique en couleur des arguments et de l'accroche
                    with col_pitch:
                    # Affichage par défaut de la matrice standard
                    pain_text = sdr_matrix[selected_sector]['pain']
                    hook_text = sdr_matrix[selected_sector]['hook']
                    
                    # Si la clé API est renseignée dans la sidebar, on affiche le bouton magique
                    if gemini_key:
                        if st.button(f"🧠 Lancer l'Analyse Live pour {data['company']}", key=f"ai_btn_{idx}"):
                            with st.spinner("Recherche Google & analyse du site en cours..."):
                                pain_text, hook_text = get_live_ai_pitch(
                                    data['company'], 
                                    selected_sector, 
                                    context_docs, 
                                    gemini_key
                                )
                    
                    st.markdown(f"⚠️ **Le 'Pain' (DCE) :** {pain_text}")
                    st.success(f"🚀 **Accroche Téléphone :** {hook_text}")

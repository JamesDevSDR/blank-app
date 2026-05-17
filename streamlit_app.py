import streamlit as st
import re
import google.generativeai as genai

# Configuration de la page en mode Large pour ton double écran
st.set_page_config(page_title="⚡ Dash'SDR", layout="wide")

st.title("⚡ Dash'SDR - Spécial DCE & Appels d'Offres")
st.caption("Version Ceinture + Bretelles : Anti-blocage et Générateur de Prompts de Secours")

# Initialisation de la mémoire Streamlit pour économiser l'API Gemini
if "live_pitches" not in st.session_state:
    st.session_state.live_pitches = {}

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

def parse_sdr_line(line):
    email_match = re.search(r'[\w.-]+@[\w.-]+\.[\w.-]+', line)
    email = email_match.group(0) if email_match else ""
    if email: line = line.replace(email, "")

    linkedin_match = re.search(r'https?://(www\.)?linkedin\.com/[^\s]+', line)
    linkedin = linkedin_match.group(0) if linkedin_match else ""
    if linkedin: line = line.replace(linkedin, "")

    phone_match = re.search(r'(?:\+?33|0)[1-9](?:[\s.-]*\d{2}){4}|\b33\d{9}\b', line)
    phone = phone_match.group(0) if phone_match else ""
    if phone: line = line.replace(phone, "")

    remaining = re.sub(r'\s+', ' ', line).strip()
    words = remaining.split(' ')
    
    if len(words) >= 2:
        prospect = f"{words[0]} {words[1]}"
        company = " ".join(words[2:]) if len(words) > 2 else "Entreprise Inconnue"
    else:
        prospect = "Non spécifié"
        company = remaining if remaining else "Entreprise Inconnue"
        
    lower_all = (company + " " + remaining).lower()
    
    keywords_bet = ['etude', 'inge', 'conseil', 'architecture', 'archi', 'bet', 'moe', "maitrise d'oeuvre", 'structure', 'economiste', 'acoustique', 'geometre', 'urbanisme', 'technique', 'solutions', 'civil engineering', 'engineering', 'genie civil', 'infra', 'superstructure', 'consulting', 'consultancy', 'architect', 'design office', 'cabinet', 'audit', 'expertise', 'amo', 'bureau d\'etudes']
    keywords_elec = ['elec', 'electricite', 'energie', 'fluide', 'spie', 'ineo', 'climatisation', 'cvc', 'chauffage', 'plomberie', 'thermique', 'cfa', 'cfo', 'courants forts', 'courants faibles', 'ventilation', 'solar', 'photovoltaique', 'sanitaire', 'genie climatique', 'engie', 'hvac', 'electricity', 'energy', 'electrical', 'plumbing', 'heating', 'lighting', 'cablage']
    keywords_second = ['peinture', 'menuis', 'sol', 'platr', 'isolation', 'facade', 'etancheite', 'vitrerie', 'serrurerie', 'metallerie', 'agencement', 'platrerie', 'faux plafond', 'carrelage', 'renovation', 'finishing', 'interior', 'painting', 'drywall', 'insulation', 'tiling', 'flooring', 'carpentry', 'fit-out', 'revetement', 'placo', 'vitrage', 'amenagement']
    keywords_gros = ['maconnerie', 'terrassement', 'demolition', 'gros oeuvre', 'fondation', 'charpente', 'beton', 'tp', 'travaux publics', 'vinci', 'eiffage construction', 'bouygues construction', 'general contractor', 'masonry', 'concrete', 'excavation', 'infrastructure', 'btp', 'construction', 'batiment', 'contractor']
    
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

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.header("🔑 Configuration de l'Agent IA")
    gemini_key = st.text_input("Colle ta clé API Gemini (Gratuite) :", type="password")
    st.caption("Si ton compte gratuit est bridé par Google, utilise le bouton de secours généré sur la fiche.")

# --- FONCTION GÉNÉRATRICE DE PROMPT (PLAN B CLIQUE & COPIE) ---
def build_fallback_prompt(company_name, sector, manual_context):
    return f"""Tu es un SDR d'élite pour l'IA Kayro dédiée au BTP. Prépare un appel de prospection téléphonique personnalisé.

PROSPECT :
- Entreprise : {company_name}
- Secteur : {sector}
- Infos site : {manual_context if manual_context else "Entreprise du secteur."}

NOTRE CATALOGUE :
{KAYRO_OFFERS_CONTEXT}

RÉPONDS STRICTEMENT SOUS CE FORMAT :
PAIN: [Analyse de 2 phrases max sur leur douleur liée aux chantiers ou appels d'offres]
HOOK: [Une seule question d'accroche percutante de moins de 15 mots]"""

# --- FONCTION AGENT DIRECT VIA API ---
def get_live_ai_pitch(company_name, sector, manual_context, api_key):
    try:
        genai.configure(api_key=api_key)
        # Utilisation de la route universelle latest pour éviter le conflit v1beta
        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
        
        prompt = build_fallback_prompt(company_name, sector, manual_context)
        response = model.generate_content(prompt)
        text = response.text
        
        pain = text.split("PAIN:")[1].split("HOOK:")[0].strip() if "PAIN:" in text else "Analyse indisponible."
        hook = text.split("HOOK:")[1].strip() if "HOOK:" in text else "Accroche indisponible."
        return pain, hook, False
    except Exception as e:
        # En cas d'échec de l'API, on renvoie l'erreur pour déclencher le mode secours
        return f"Erreur Quota Google ({str(e)})", "", True

# --- INTERFACE GRAPHIQUE PRINCIPALE ---
raw_input = st.text_area(
    "1. Colle ici ta ligne ou ta liste de prospects copiée d'Excel / CRM :", 
    height=120, 
    placeholder="Exemple :\nPhilippe Baudry Artea BTP 33609288487 philippe@arteia.com"
)

if raw_input:
    lines = [l.strip() for l in raw_input.split('\n') if l.strip()]
    
    if lines:
        st.markdown("---")
        st.subheader("🎯 Tes Fiches d'Appels Personnalisées")
        
        for idx, current_line in enumerate(lines):
            data = parse_sdr_line(current_line)
            company_key = f"{data['company']}_{idx}"
            
            with st.container(border=True):
                col_info, col_sector, col_pitch = st.columns([3, 3, 5])
                
                with col_info:
                    st.markdown(f"### 👤 {data['prospect']}")
                    st.markdown(f"**🏢 Entreprise :** `{data['company']}`")
                    
                    contacts = []
                    if data['phone']: contacts.append(f"📞 **{data['phone']}**")
                    if data['email']: contacts.append(f"✉️ [Mail](mailto:{data['email']})")
                    if data['linkedin']: contacts.append(f"🔗 [LinkedIn]({data['linkedin']})")
                    if contacts: st.markdown(" | ".join(contacts))
                    else: st.caption("Aucune coordonnée détectée")
                
                with col_sector:
                    selected_sector = st.selectbox(
                        f"Ajuster le secteur de {data['company']}", 
                        list(sdr_matrix.keys()), 
                        index=list(sdr_matrix.keys()).index(data['sector']),
                        key=f"select_{idx}"
                    )
                    
                    company_note = st.text_input(
                        "🔗 Optionnel : Note sur l'activité",
                        key=f"note_{idx}",
                        placeholder="Ex: Rénovation, gros marchés..."
                    )
                
                with col_pitch:
                    is_blocked = False
                    if company_key in st.session_state.live_pitches:
                        pain_text, hook_text = st.session_state.live_pitches[company_key]
                    else:
                        pain_text = sdr_matrix[selected_sector]['pain']
                        hook_text = sdr_matrix[selected_sector]['hook']
                    
                    if gemini_key:
                        if st.button(f"🧠 Lancer l'Analyse Live pour {data['company']}", key=f"ai_btn_{idx}"):
                            with st.spinner("Calcul en cours..."):
                                res_pain, res_hook, error_triggered = get_live_ai_pitch(
                                    data['company'], selected_sector, company_note, gemini_key
                                )
                                if not error_triggered:
                                    pain_text, hook_text = res_pain, res_hook
                                    st.session_state.live_pitches[company_key] = (pain_text, hook_text)
                                else:
                                    is_blocked = True
                                    pain_text = res_pain

                    st.markdown(f"⚠️ **Le 'Pain' (DCE) :** {pain_text}")
                    if hook_text:
                        st.success(f"🚀 **Accroche Téléphone :** {hook_text}")
                    
                    # BLOC DE SECOURS AUTOMATIQUE EN CAS DE BLOCAGE QUOTA GOOGLE
                    if "Erreur Quota" in pain_text or is_blocked:
                        st.info("💡 **Plan B activé :** Google bloque ton API, mais le prompt sur-mesure a été généré ci-dessous. Copie-le et colle-le directement dans [Gemini Web Gratuit](https://gemini.google.com/) pour obtenir ton accroche immédiate.")
                        text_prompt_fallback = build_fallback_prompt(data['company'], selected_sector, company_note)
                        st.text_area("📋 Copie ce texte :", value=text_prompt_fallback, height=150, key=f"fallback_area_{idx}")

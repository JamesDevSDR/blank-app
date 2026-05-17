import streamlit as st
import re

# Configuration de la page en mode Large pour ton double écran
st.set_page_config(page_title="⚡ Dash'SDR", layout="wide")

st.title("⚡ Dash'SDR - Spécial DCE & Appels d'Offres")
st.caption("Outil de structuration de données CRM & Alignement de valeur instantané")

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
    
    # LOGIQUE DE TRI PAR PRIORITÉ (Élimine le problème du mot "BTP" global)
    if any(x in lower_all for x in keywords_bet):
        sector = "📐 Bureau d'Études / Ingénierie / Archi"
    elif any(x in lower_all for x in keywords_elec):
        sector = "⚡ Électricité / Fluides / CVC"
    elif any(x in lower_all for x in keywords_second):
        sector = "🛠️ Second Œuvre / Finitions"
    elif any(x in lower_all for x in keywords_gros):
        sector = "🧱 Gros Œuvre / BTP"
    else:
        # Sécurité si aucun mot de la matrice n'est trouvé
        sector = "🧱 Gros Œuvre / BTP"

    return {
        "prospect": prospect,
        "company": company,
        "email": email,
        "linkedin": linkedin,
        "phone": phone,
        "sector": sector
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
                    st.markdown(f"⚠️ **Le 'Pain' (DCE) :** {sdr_matrix[selected_sector]['pain']}")
                    st.success(f"🚀 **Accroche Téléphone :** {sdr_matrix[selected_sector]['hook']}")

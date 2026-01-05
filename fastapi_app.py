from fastapi import FastAPI, UploadFile, File, HTTPException
import pdfplumber
import json
import io
from google import genai
from google.genai import types  # Import pour la configuration JSON

# Configuration du client
client = genai.Client(api_key="TON_CLE_API")

app = FastAPI()


def analyser_cahier_des_charges(texte: str):
    prompt = f"""
    Tu es un expert en gestion de projet et ingénieur logiciel senior.
    Analyse le cahier des charges fourni pour décomposer le projet en tâches techniques précises.
    
    Pour chaque tâche :
    1. Estime le temps nécessaire (en jours-homme).
    2. Identifie les compétences spécifiques requises.
    3. Évalue le coût global et le délai total de livraison.
    
    TEXTE DU CAHIER DES CHARGES :
    {texte}
    """

    # Nouveau schéma détaillé
    response = client.models.generate_content(
        model="gemini-2.5-flash",  # ou gemini-1.5-flash
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "nom_projet": {"type": "STRING"},
                    "resume_executif": {"type": "STRING"},
                    "taches_techniques": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "description": {"type": "STRING"},
                                "temps_estime_jours": {"type": "NUMBER"},
                                "competences_requises": {"type": "ARRAY", "items": {"type": "STRING"}},
                                # ex: Faible, Moyenne, Haute
                                "complexite": {"type": "STRING"}
                            }
                        }
                    },
                    "estimation_globale": {
                        "type": "OBJECT",
                        "properties": {
                            "temps_total_jours": {"type": "NUMBER"},
                            # ex: 3 mois après début
                            "date_livraison_estimee": {"type": "STRING"},
                            "cout_total_estime_euros": {"type": "NUMBER"},
                            "justification_cout": {"type": "STRING"}
                        }
                    },
                    "competences_cles_equipe": {"type": "ARRAY", "items": {"type": "STRING"}}
                }
            }
        )
    )

    return json.loads(response.text)


@app.post("/analyse-pdf")
async def analyse_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Fichier PDF requis")

    try:
        # Lire le contenu du fichier en mémoire
        content = await file.read()
        pdf_file = io.BytesIO(content)

        texte = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                texte += page.extract_text() or ""

        if not texte.strip():
            raise HTTPException(
                status_code=400, detail="PDF vide ou illisible")

        # Gemini 1.5 Flash supporte jusqu'à 1 million de tokens,
        # tu peux envoyer bien plus que 6000 caractères !
        resultat = analyser_cahier_des_charges(texte)
        return resultat

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


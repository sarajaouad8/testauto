"""
Script de test pour vérifier que tout fonctionne
"""
print("🔍 Test de connexion Gemini...")

try:
    from google import genai
    from google.genai import types
    print("✅ Import google-genai réussi")
except ImportError as e:
    print(f"❌ Erreur import: {e}")
    print("Installe avec: pip install google-genai")
    exit(1)

# Test de connexion
API_KEY = "AIzaSyABodZJw01EzhiHwvXI91Mb72tX0865NFU"

try:
    client = genai.Client(api_key=API_KEY)
    print("✅ Client créé")
    
    # Test simple
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents="Réponds juste: OK"
    )
    print(f"✅ Réponse Gemini: {response.text}")
    
except Exception as e:
    print(f"❌ Erreur: {type(e).__name__}: {e}")

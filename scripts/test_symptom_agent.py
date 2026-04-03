from backend.agents.symptom_extraction_agent import SymptomExtractionAgent
agent = SymptomExtractionAgent()
symptoms = agent.extract("I've had a 38.5°C fever and a splitting headache for 2 days")
for s in symptoms:
    print(s.name, s.severity, s.duration)
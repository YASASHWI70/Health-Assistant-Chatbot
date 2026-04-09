from backend.agents.symptom_extraction_agent import SymptomExtractionAgent
agent = SymptomExtractionAgent()
symptoms = agent.extract("What is the difference between a raw OpenAI call and using LangChain?")
for s in symptoms:
    print(s.name, s.severity, s.duration)
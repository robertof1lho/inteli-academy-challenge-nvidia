# Entry point do backend (CrewAI runner)
from pipelines.startup_pipeline import StartupPipeline

if __name__ == "__main__":
    pipeline = StartupPipeline()
    result = pipeline.run("Startups de IA em saúde na América Latina")

    print("Resultado estruturado:")
    print(result["structured"])
    print("SQL sugerido:")
    print(result["sql"])

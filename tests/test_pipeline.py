from src.backend.pipelines.startup_pipeline import StartupPipeline

def test_pipeline():
    pipeline = StartupPipeline()
    result = pipeline.run("Startups de IA em saúde na América Latina")
    
    assert "raw" in result
    assert "structured" in result
    assert "sql" in result
    
    print("🔎 Pesquisa bruta:", result["raw"])
    print("🧠 Estruturado:", result["structured"])
    print("📊 SQL gerado:", result["sql"])

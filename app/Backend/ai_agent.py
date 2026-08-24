import os
from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from app.Backend.schemas import SozlesmeRaporu

os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"
yerel_model = OllamaModel(model_name='qwen3.5:9b')

analist_ajan = Agent(
    model=yerel_model,
    output_type=SozlesmeRaporu, 
    system_prompt=(
        "Sen uzman bir kurumsal sözleşme analistisin. "
        "Görevlerin şunlardır: "
        "1. Sana verilen sözleşme metnini dikkatlice oku; tarafları, tarihleri ve sözleşmenin konusunu çıkar. "
        "2. Şirket için tehlike veya mali yükümlülük yaratabilecek yasal riskleri tespit et ve bu riskleri 1 ile 10 arasında puanla. "
        "3. Çıktıyı tam olarak istenen veri yapısına (schema) uygun şekilde üret. "
        "Ekstra sohbet veya yorum ekleme, sadece istenen yapılandırılmış verileri doldur."
    )
)
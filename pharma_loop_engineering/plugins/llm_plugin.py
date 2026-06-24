"""LLM plugin for interacting with Qwen language models via DashScope/OpenRouter."""
from typing import Dict, Any, List, Optional
from loguru import logger
from utils.llm_utils import call_llm
import asyncio

class LLMPlugin:
    """Plugin for LLM interactions using Qwen models via DashScope or OpenRouter."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # Default to dashscope provider for Qwen models
        self.provider = config.get("provider", "dashscope")

    async def generate_text(self, prompt: str, max_tokens: int = 1000, role: str = "reasoning") -> str:
        """Generate text using Qwen LLM."""
        logger.info(f"Generating text with Qwen {role} model via {self.provider}")
        try:
            return await call_llm(prompt, role=role)
        except Exception as e:
            logger.error(f"Qwen LLM generation failed: {e}")
            return ""

    async def chat_completion(self, messages: List[Dict[str, str]], role: str = "reasoning") -> str:
        """Chat completion with conversation history using Qwen models."""
        logger.info(f"Running Qwen chat completion with {role} model via {self.provider}")
        try:
            # Convert messages to prompt format
            prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            return await call_llm(prompt, role=role)
        except Exception as e:
            logger.error(f"Qwen chat completion failed: {e}")
            return ""

    def embed_text(self, text: str) -> List[float]:
        """Generate text embeddings using Qwen embeddings model."""
        logger.info("Generating Qwen embeddings")
        # Note: This would need implementation for actual embeddings API
        return []

    # Synchronous wrappers for backward compatibility
    def generate_text_sync(self, prompt: str, max_tokens: int = 1000, role: str = "reasoning") -> str:
        """Synchronous wrapper for generate_text."""
        return asyncio.run(self.generate_text(prompt, max_tokens, role))

    def chat_completion_sync(self, messages: List[Dict[str, str]], role: str = "reasoning") -> str:
        """Synchronous wrapper for chat_completion."""
        return asyncio.run(self.chat_completion(messages, role))
<task_progress>
- [x] PASO 1: Auditoría de modelos actuales (completado)
- [x] PASO 2: Actualizar config/settings.py con distribución Qwen (completado)
- [x] PASO 3: Actualizar utils/llm_utils.py (completado)
- [x] PASO 4: Asignar modelo correcto en cada agente (completado)
- [x] PASO 5: Actualizar .env.example (completado)
- [ ] PASO 6: Verificación final (en progreso)
</task_progress>
</write_to_file>
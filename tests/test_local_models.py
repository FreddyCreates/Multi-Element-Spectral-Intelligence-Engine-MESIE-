"""Tests for mesie.ai.local_models — type-safe local model interface."""

import pytest

from mesie.ai.local_models import (
    ChatMessage,
    EmbeddingResponse,
    GenerationParams,
    GenerationResponse,
    LocalModelBackend,
    LocalModelClient,
    LocalModelConfig,
    MessageRole,
    ModelCapability,
    ModelProvider,
    OllamaBackend,
    SpectralContext,
    StopReason,
    StreamChunk,
    TokenUsage,
    register_backend,
)


# =============================================================================
# Configuration tests
# =============================================================================


class TestLocalModelConfig:
    def test_defaults(self):
        config = LocalModelConfig()
        assert config.provider == ModelProvider.OLLAMA
        assert config.model_name == "llama3"
        assert config.host == "127.0.0.1"
        assert config.port == 11434
        assert config.context_length == 4096

    def test_base_url(self):
        config = LocalModelConfig(host="localhost", port=8080)
        assert config.base_url == "http://localhost:8080"

    def test_supports_capability(self):
        config = LocalModelConfig(
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.EMBEDDINGS]
        )
        assert config.supports(ModelCapability.TEXT_GENERATION)
        assert config.supports(ModelCapability.EMBEDDINGS)
        assert not config.supports(ModelCapability.VISION)

    def test_custom_provider(self):
        config = LocalModelConfig(provider=ModelProvider.CUSTOM, model_name="my-model")
        assert config.provider == ModelProvider.CUSTOM


# =============================================================================
# GenerationParams tests
# =============================================================================


class TestGenerationParams:
    def test_defaults(self):
        params = GenerationParams()
        assert params.temperature == 0.7
        assert params.top_p == 0.9
        assert params.top_k == 40
        assert params.max_tokens == 1024

    def test_invalid_temperature(self):
        with pytest.raises(ValueError, match="temperature must be >= 0.0"):
            GenerationParams(temperature=-0.1)

    def test_invalid_top_p(self):
        with pytest.raises(ValueError, match="top_p must be in"):
            GenerationParams(top_p=0.0)
        with pytest.raises(ValueError, match="top_p must be in"):
            GenerationParams(top_p=1.5)

    def test_invalid_top_k(self):
        with pytest.raises(ValueError, match="top_k must be >= 0"):
            GenerationParams(top_k=-1)

    def test_invalid_max_tokens(self):
        with pytest.raises(ValueError, match="max_tokens must be >= 1"):
            GenerationParams(max_tokens=0)

    def test_valid_params(self):
        params = GenerationParams(
            temperature=0.0, top_p=1.0, top_k=0, max_tokens=1, seed=42
        )
        assert params.seed == 42
        assert params.temperature == 0.0


# =============================================================================
# ChatMessage tests
# =============================================================================


class TestChatMessage:
    def test_system_factory(self):
        msg = ChatMessage.system("You are helpful.")
        assert msg.role == MessageRole.SYSTEM
        assert msg.content == "You are helpful."

    def test_user_factory(self):
        msg = ChatMessage.user("Hello")
        assert msg.role == MessageRole.USER

    def test_assistant_factory(self):
        msg = ChatMessage.assistant("Hi there")
        assert msg.role == MessageRole.ASSISTANT

    def test_to_dict(self):
        msg = ChatMessage.user("test", key="value")
        d = msg.to_dict()
        assert d["role"] == "user"
        assert d["content"] == "test"
        assert d["metadata"] == {"key": "value"}

    def test_to_dict_no_metadata(self):
        msg = ChatMessage.user("test")
        d = msg.to_dict()
        assert "metadata" not in d


# =============================================================================
# Response types tests
# =============================================================================


class TestGenerationResponse:
    def test_tokens_per_second(self):
        resp = GenerationResponse(
            text="hello",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=50, total_tokens=60),
            latency_ms=1000.0,
        )
        assert resp.tokens_per_second == pytest.approx(50.0)

    def test_tokens_per_second_zero_latency(self):
        resp = GenerationResponse(text="hello", latency_ms=0.0)
        assert resp.tokens_per_second == 0.0

    def test_stop_reason(self):
        resp = GenerationResponse(text="x", stop_reason=StopReason.MAX_TOKENS)
        assert resp.stop_reason == StopReason.MAX_TOKENS


class TestEmbeddingResponse:
    def test_auto_dimensions(self):
        resp = EmbeddingResponse(embedding=[1.0, 2.0, 3.0])
        assert resp.dimensions == 3

    def test_explicit_dimensions(self):
        resp = EmbeddingResponse(embedding=[1.0, 2.0], dimensions=2)
        assert resp.dimensions == 2


class TestTokenUsage:
    def test_defaults(self):
        usage = TokenUsage()
        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0
        assert usage.total_tokens == 0


# =============================================================================
# SpectralContext tests
# =============================================================================


class TestSpectralContext:
    def test_to_prompt_context(self):
        ctx = SpectralContext(
            frequency_range=(0.5, 50.0),
            peak_frequencies=[2.3, 8.1, 15.0],
            spectral_summary="Three dominant peaks in low-frequency range",
            record_id="rec_001",
        )
        text = ctx.to_prompt_context()
        assert "[Spectral Context]" in text
        assert "0.50–50.00 Hz" in text
        assert "2.30 Hz" in text
        assert "rec_001" in text
        assert "Three dominant" in text

    def test_minimal_context(self):
        ctx = SpectralContext()
        text = ctx.to_prompt_context()
        assert "[Spectral Context]" in text
        assert "0.00–100.00 Hz" in text


# =============================================================================
# Mock backend for client tests
# =============================================================================


class MockBackend(LocalModelBackend):
    """Mock backend for testing the client without a real model."""

    def __init__(self, config: LocalModelConfig) -> None:
        super().__init__(config)
        self.generate_calls: list = []
        self.chat_calls: list = []
        self.embed_calls: list = []

    def generate(self, prompt, params):
        self.generate_calls.append((prompt, params))
        return GenerationResponse(
            text=f"Generated: {prompt[:20]}",
            stop_reason=StopReason.END_OF_SEQUENCE,
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model_name=self.config.model_name,
            latency_ms=50.0,
        )

    def chat(self, messages, params):
        self.chat_calls.append((messages, params))
        return GenerationResponse(
            text="Chat response",
            model_name=self.config.model_name,
            latency_ms=60.0,
        )

    def embed(self, text):
        self.embed_calls.append(text)
        return EmbeddingResponse(
            embedding=[0.1, 0.2, 0.3, 0.4],
            model_name=self.config.model_name,
            latency_ms=10.0,
        )

    def stream(self, prompt, params):
        yield StreamChunk(text="Hello", done=False)
        yield StreamChunk(text=" world", done=True, usage=TokenUsage(total_tokens=5))

    def health_check(self):
        return True

    def list_models(self):
        return ["mock-model-1", "mock-model-2"]


# =============================================================================
# LocalModelClient tests (with mock backend)
# =============================================================================


class TestLocalModelClient:
    def _make_client(self) -> tuple:
        config = LocalModelConfig(model_name="test-model")
        backend = MockBackend(config)
        client = LocalModelClient(config, backend=backend)
        return client, backend

    def test_generate(self):
        client, backend = self._make_client()
        resp = client.generate("Hello world")
        assert resp.text.startswith("Generated:")
        assert len(backend.generate_calls) == 1

    def test_generate_with_spectral_context(self):
        client, backend = self._make_client()
        ctx = SpectralContext(peak_frequencies=[5.0, 10.0])
        resp = client.generate("Analyze", spectral_context=ctx)
        prompt_sent = backend.generate_calls[0][0]
        assert "[Spectral Context]" in prompt_sent
        assert "Analyze" in prompt_sent

    def test_generate_with_params(self):
        client, backend = self._make_client()
        params = GenerationParams(temperature=0.1, max_tokens=100)
        resp = client.generate("test", params=params)
        assert backend.generate_calls[0][1].temperature == 0.1

    def test_chat(self):
        client, backend = self._make_client()
        messages = [
            ChatMessage.system("Be helpful"),
            ChatMessage.user("Hi"),
        ]
        resp = client.chat(messages)
        assert resp.text == "Chat response"
        assert len(backend.chat_calls) == 1

    def test_chat_with_spectral_context(self):
        client, backend = self._make_client()
        ctx = SpectralContext(spectral_summary="Test spectrum")
        messages = [ChatMessage.user("Analyze")]
        resp = client.chat(messages, spectral_context=ctx)
        sent_messages = backend.chat_calls[0][0]
        # Spectral context should be injected as first system message
        assert sent_messages[0].role == MessageRole.SYSTEM
        assert "Test spectrum" in sent_messages[0].content

    def test_embed(self):
        client, backend = self._make_client()
        resp = client.embed("test text")
        assert resp.embedding == [0.1, 0.2, 0.3, 0.4]
        assert resp.dimensions == 4
        assert backend.embed_calls == ["test text"]

    def test_stream(self):
        client, _ = self._make_client()
        chunks = list(client.stream("Hello"))
        assert len(chunks) == 2
        assert chunks[0].text == "Hello"
        assert chunks[0].done is False
        assert chunks[1].text == " world"
        assert chunks[1].done is True

    def test_health_check(self):
        client, _ = self._make_client()
        assert client.health_check() is True

    def test_list_models(self):
        client, _ = self._make_client()
        models = client.list_models()
        assert "mock-model-1" in models

    def test_repr(self):
        client, _ = self._make_client()
        r = repr(client)
        assert "LocalModelClient" in r
        assert "test-model" in r

    def test_provider_property(self):
        client, _ = self._make_client()
        assert client.provider == ModelProvider.OLLAMA

    def test_model_name_property(self):
        client, _ = self._make_client()
        assert client.model_name == "test-model"

    def test_analyze_spectrum(self):
        client, backend = self._make_client()
        ctx = SpectralContext(
            peak_frequencies=[2.5, 7.0],
            spectral_summary="Low-frequency peaks",
        )
        resp = client.analyze_spectrum(ctx)
        assert resp.text == "Chat response"
        # Should have called chat with system + context + user messages
        msgs = backend.chat_calls[0][0]
        assert len(msgs) == 3
        assert msgs[0].role == MessageRole.SYSTEM
        assert "MESIE" in msgs[0].content


# =============================================================================
# Backend registry tests
# =============================================================================


class TestBackendRegistry:
    def test_register_custom_backend(self):
        register_backend(ModelProvider.CUSTOM, MockBackend)
        config = LocalModelConfig(provider=ModelProvider.CUSTOM, model_name="custom")
        client = LocalModelClient(config)
        assert client.health_check() is True

    def test_unregistered_provider_raises(self):
        config = LocalModelConfig(provider=ModelProvider.LLAMA_CPP)
        with pytest.raises(ValueError, match="No backend registered"):
            LocalModelClient(config)

    def test_register_non_subclass_raises(self):
        with pytest.raises(TypeError, match="must subclass"):
            register_backend(ModelProvider.CUSTOM, dict)  # type: ignore


# =============================================================================
# ModelProvider / ModelCapability enum tests
# =============================================================================


class TestEnums:
    def test_model_provider_values(self):
        assert ModelProvider.OLLAMA.value == "ollama"
        assert ModelProvider.LLAMA_CPP.value == "llama_cpp"
        assert ModelProvider.HUGGINGFACE_LOCAL.value == "huggingface_local"

    def test_model_capability_values(self):
        assert ModelCapability.SPECTRAL_ANALYSIS.value == "spectral_analysis"

    def test_stop_reason_values(self):
        assert StopReason.END_OF_SEQUENCE.value == "end_of_sequence"
        assert StopReason.MAX_TOKENS.value == "max_tokens"

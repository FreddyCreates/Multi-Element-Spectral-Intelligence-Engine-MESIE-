"""Local Models — Clean, type-safe interface for interacting with local models.

Provides a unified, provider-agnostic interface to interact with locally-hosted
AI models (e.g., Ollama, llama.cpp, vLLM local, HuggingFace local pipelines)
integrated with MESIE's spectral intelligence primitives.

Key Design Principles:
- **Type-safe**: All inputs and outputs are fully typed with dataclasses/enums.
- **Provider-agnostic**: Swap backends (Ollama, llama.cpp, HuggingFace local)
  without changing application code.
- **MESIE-native**: First-class support for spectral context, embeddings, and
  structured reasoning about spectral data.
- **Zero cloud dependency**: All inference runs entirely on-device.
- **Streaming support**: Async-ready streaming for real-time generation.

Example:
    >>> from mesie.ai.local_models import LocalModelClient, LocalModelConfig, ModelProvider
    >>> config = LocalModelConfig(provider=ModelProvider.OLLAMA, model_name="llama3")
    >>> client = LocalModelClient(config)
    >>> response = client.generate("Analyze this spectral pattern", temperature=0.7)
    >>> print(response.text)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Iterator, List, Optional, Sequence


# =============================================================================
# Enumerations
# =============================================================================


class ModelProvider(Enum):
    """Supported local model providers."""

    OLLAMA = "ollama"
    LLAMA_CPP = "llama_cpp"
    HUGGINGFACE_LOCAL = "huggingface_local"
    VLLM_LOCAL = "vllm_local"
    CUSTOM = "custom"


class ModelCapability(Enum):
    """Capabilities a local model may support."""

    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    EMBEDDINGS = "embeddings"
    CODE_GENERATION = "code_generation"
    FUNCTION_CALLING = "function_calling"
    VISION = "vision"
    SPECTRAL_ANALYSIS = "spectral_analysis"


class StopReason(Enum):
    """Reason the model stopped generating."""

    END_OF_SEQUENCE = "end_of_sequence"
    MAX_TOKENS = "max_tokens"
    STOP_SEQUENCE = "stop_sequence"
    ERROR = "error"


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class LocalModelConfig:
    """Configuration for a local model connection.

    Args:
        provider: Which local inference backend to use.
        model_name: Name/path of the model to load.
        host: Host address for server-based providers (e.g., Ollama).
        port: Port number for server-based providers.
        model_path: Filesystem path for file-based providers (e.g., GGUF files).
        context_length: Maximum context window size in tokens.
        n_gpu_layers: Number of layers to offload to GPU (-1 = all).
        n_threads: Number of CPU threads for inference.
        capabilities: Declared capabilities of this model.
        timeout_seconds: Request timeout in seconds.
        retry_attempts: Number of retries on transient failures.
    """

    provider: ModelProvider = ModelProvider.OLLAMA
    model_name: str = "llama3"
    host: str = "127.0.0.1"
    port: int = 11434
    model_path: Optional[str] = None
    context_length: int = 4096
    n_gpu_layers: int = -1
    n_threads: int = 4
    capabilities: List[ModelCapability] = field(
        default_factory=lambda: [ModelCapability.TEXT_GENERATION, ModelCapability.CHAT]
    )
    timeout_seconds: float = 120.0
    retry_attempts: int = 2

    @property
    def base_url(self) -> str:
        """Construct the base URL for server-based providers."""
        return f"http://{self.host}:{self.port}"

    def supports(self, capability: ModelCapability) -> bool:
        """Check whether this model configuration declares a given capability."""
        return capability in self.capabilities


# =============================================================================
# Message types for chat interface
# =============================================================================


class MessageRole(Enum):
    """Role of a message in a conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class ChatMessage:
    """A single message in a chat conversation.

    Args:
        role: Who sent this message.
        content: The text content of the message.
        metadata: Optional metadata (tool calls, spectral context, etc.).
    """

    role: MessageRole
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def system(cls, content: str, **meta: Any) -> "ChatMessage":
        """Create a system message."""
        return cls(role=MessageRole.SYSTEM, content=content, metadata=meta)

    @classmethod
    def user(cls, content: str, **meta: Any) -> "ChatMessage":
        """Create a user message."""
        return cls(role=MessageRole.USER, content=content, metadata=meta)

    @classmethod
    def assistant(cls, content: str, **meta: Any) -> "ChatMessage":
        """Create an assistant message."""
        return cls(role=MessageRole.ASSISTANT, content=content, metadata=meta)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a provider-agnostic dict."""
        d: Dict[str, Any] = {"role": self.role.value, "content": self.content}
        if self.metadata:
            d["metadata"] = self.metadata
        return d


# =============================================================================
# Generation parameters
# =============================================================================


@dataclass
class GenerationParams:
    """Parameters controlling text generation.

    Args:
        temperature: Sampling temperature (0.0 = greedy, higher = more random).
        top_p: Nucleus sampling threshold.
        top_k: Top-k sampling limit (0 = disabled).
        max_tokens: Maximum tokens to generate.
        stop_sequences: Sequences that halt generation.
        repeat_penalty: Penalty for repeated tokens.
        seed: Random seed for reproducibility (None = non-deterministic).
        frequency_penalty: Penalize frequent tokens.
        presence_penalty: Penalize tokens already present.
    """

    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    max_tokens: int = 1024
    stop_sequences: List[str] = field(default_factory=list)
    repeat_penalty: float = 1.1
    seed: Optional[int] = None
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    def __post_init__(self) -> None:
        if self.temperature < 0.0:
            raise ValueError("temperature must be >= 0.0")
        if not (0.0 < self.top_p <= 1.0):
            raise ValueError("top_p must be in (0.0, 1.0]")
        if self.top_k < 0:
            raise ValueError("top_k must be >= 0")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be >= 1")


# =============================================================================
# Response types
# =============================================================================


@dataclass
class TokenUsage:
    """Token usage statistics for a generation call.

    Args:
        prompt_tokens: Tokens in the input prompt.
        completion_tokens: Tokens generated.
        total_tokens: Total tokens (prompt + completion).
    """

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class GenerationResponse:
    """Response from a local model generation call.

    Args:
        text: The generated text content.
        stop_reason: Why the model stopped generating.
        usage: Token usage statistics.
        model_name: Which model produced this response.
        latency_ms: End-to-end latency in milliseconds.
        metadata: Provider-specific metadata.
    """

    text: str
    stop_reason: StopReason = StopReason.END_OF_SEQUENCE
    usage: TokenUsage = field(default_factory=TokenUsage)
    model_name: str = ""
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def tokens_per_second(self) -> float:
        """Compute generation throughput."""
        if self.latency_ms <= 0 or self.usage.completion_tokens <= 0:
            return 0.0
        return (self.usage.completion_tokens / self.latency_ms) * 1000.0


@dataclass
class EmbeddingResponse:
    """Response from a local model embedding call.

    Args:
        embedding: The computed embedding vector.
        model_name: Which model produced this embedding.
        dimensions: Dimensionality of the embedding.
        latency_ms: End-to-end latency in milliseconds.
    """

    embedding: List[float]
    model_name: str = ""
    dimensions: int = 0
    latency_ms: float = 0.0

    def __post_init__(self) -> None:
        if self.dimensions == 0:
            self.dimensions = len(self.embedding)


@dataclass
class StreamChunk:
    """A single chunk from a streaming generation response.

    Args:
        text: The text fragment in this chunk.
        done: Whether this is the final chunk.
        usage: Token usage (populated on final chunk).
    """

    text: str
    done: bool = False
    usage: Optional[TokenUsage] = None


# =============================================================================
# Spectral context integration
# =============================================================================


@dataclass
class SpectralContext:
    """Spectral context to inject into model prompts for MESIE integration.

    Args:
        frequency_range: Frequency range of the spectral data (Hz).
        peak_frequencies: Dominant peak frequencies identified.
        spectral_summary: Human-readable summary of the spectral signature.
        embedding_vector: Optional MESIE embedding vector for RAG-style retrieval.
        record_id: Optional MESIE record identifier for lineage.
    """

    frequency_range: tuple[float, float] = (0.0, 100.0)
    peak_frequencies: List[float] = field(default_factory=list)
    spectral_summary: str = ""
    embedding_vector: Optional[List[float]] = None
    record_id: Optional[str] = None

    def to_prompt_context(self) -> str:
        """Format the spectral context as a prompt injection string."""
        parts = [f"[Spectral Context]"]
        parts.append(f"Frequency range: {self.frequency_range[0]:.2f}–{self.frequency_range[1]:.2f} Hz")
        if self.peak_frequencies:
            peaks = ", ".join(f"{f:.2f} Hz" for f in self.peak_frequencies[:10])
            parts.append(f"Peak frequencies: {peaks}")
        if self.spectral_summary:
            parts.append(f"Summary: {self.spectral_summary}")
        if self.record_id:
            parts.append(f"Record ID: {self.record_id}")
        return "\n".join(parts)


# =============================================================================
# Provider backends (protocol-style base)
# =============================================================================


class LocalModelBackend:
    """Abstract backend interface for local model providers.

    Subclass this to implement a new provider integration.
    All methods raise NotImplementedError by default.
    """

    def __init__(self, config: LocalModelConfig) -> None:
        self.config = config

    def generate(
        self, prompt: str, params: GenerationParams
    ) -> GenerationResponse:
        """Generate text from a prompt."""
        raise NotImplementedError(
            f"generate() not implemented for {self.config.provider.value}"
        )

    def chat(
        self, messages: List[ChatMessage], params: GenerationParams
    ) -> GenerationResponse:
        """Chat-style completion from a message list."""
        raise NotImplementedError(
            f"chat() not implemented for {self.config.provider.value}"
        )

    def embed(self, text: str) -> EmbeddingResponse:
        """Compute an embedding for the given text."""
        raise NotImplementedError(
            f"embed() not implemented for {self.config.provider.value}"
        )

    def stream(
        self, prompt: str, params: GenerationParams
    ) -> Iterator[StreamChunk]:
        """Stream text generation chunk by chunk."""
        raise NotImplementedError(
            f"stream() not implemented for {self.config.provider.value}"
        )

    def health_check(self) -> bool:
        """Check whether the backend is reachable and ready."""
        return False

    def list_models(self) -> List[str]:
        """List available models on this backend."""
        return []


# =============================================================================
# Ollama backend
# =============================================================================


class OllamaBackend(LocalModelBackend):
    """Backend implementation for Ollama local inference server.

    Communicates with the Ollama REST API at the configured host:port.
    Requires Ollama to be running locally (``ollama serve``).
    """

    def generate(
        self, prompt: str, params: GenerationParams
    ) -> GenerationResponse:
        """Generate text via Ollama /api/generate endpoint."""
        import json
        import urllib.request
        import urllib.error

        url = f"{self.config.base_url}/api/generate"
        payload = {
            "model": self.config.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": params.temperature,
                "top_p": params.top_p,
                "top_k": params.top_k,
                "num_predict": params.max_tokens,
                "repeat_penalty": params.repeat_penalty,
            },
        }
        if params.stop_sequences:
            payload["options"]["stop"] = params.stop_sequences
        if params.seed is not None:
            payload["options"]["seed"] = params.seed

        start = time.perf_counter()
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as resp:
                result = json.loads(resp.read().decode())
        except (urllib.error.URLError, OSError) as exc:
            return GenerationResponse(
                text="",
                stop_reason=StopReason.ERROR,
                model_name=self.config.model_name,
                metadata={"error": str(exc)},
            )
        latency = (time.perf_counter() - start) * 1000

        text = result.get("response", "")
        done_reason = result.get("done_reason", "stop")
        stop_reason = (
            StopReason.MAX_TOKENS
            if done_reason == "length"
            else StopReason.END_OF_SEQUENCE
        )

        prompt_tokens = result.get("prompt_eval_count", 0)
        completion_tokens = result.get("eval_count", 0)

        return GenerationResponse(
            text=text,
            stop_reason=stop_reason,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            model_name=self.config.model_name,
            latency_ms=latency,
            metadata={"raw_response": result},
        )

    def chat(
        self, messages: List[ChatMessage], params: GenerationParams
    ) -> GenerationResponse:
        """Chat via Ollama /api/chat endpoint."""
        import json
        import urllib.request
        import urllib.error

        url = f"{self.config.base_url}/api/chat"
        payload = {
            "model": self.config.model_name,
            "messages": [m.to_dict() for m in messages],
            "stream": False,
            "options": {
                "temperature": params.temperature,
                "top_p": params.top_p,
                "top_k": params.top_k,
                "num_predict": params.max_tokens,
                "repeat_penalty": params.repeat_penalty,
            },
        }
        if params.stop_sequences:
            payload["options"]["stop"] = params.stop_sequences
        if params.seed is not None:
            payload["options"]["seed"] = params.seed

        start = time.perf_counter()
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as resp:
                result = json.loads(resp.read().decode())
        except (urllib.error.URLError, OSError) as exc:
            return GenerationResponse(
                text="",
                stop_reason=StopReason.ERROR,
                model_name=self.config.model_name,
                metadata={"error": str(exc)},
            )
        latency = (time.perf_counter() - start) * 1000

        message = result.get("message", {})
        text = message.get("content", "")
        done_reason = result.get("done_reason", "stop")
        stop_reason = (
            StopReason.MAX_TOKENS
            if done_reason == "length"
            else StopReason.END_OF_SEQUENCE
        )

        prompt_tokens = result.get("prompt_eval_count", 0)
        completion_tokens = result.get("eval_count", 0)

        return GenerationResponse(
            text=text,
            stop_reason=stop_reason,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            model_name=self.config.model_name,
            latency_ms=latency,
        )

    def embed(self, text: str) -> EmbeddingResponse:
        """Compute embedding via Ollama /api/embed endpoint."""
        import json
        import urllib.request
        import urllib.error

        url = f"{self.config.base_url}/api/embed"
        payload = {"model": self.config.model_name, "input": text}

        start = time.perf_counter()
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as resp:
                result = json.loads(resp.read().decode())
        except (urllib.error.URLError, OSError) as exc:
            return EmbeddingResponse(embedding=[], model_name=self.config.model_name)
        latency = (time.perf_counter() - start) * 1000

        embeddings = result.get("embeddings", [[]])
        vec = embeddings[0] if embeddings else []

        return EmbeddingResponse(
            embedding=vec,
            model_name=self.config.model_name,
            latency_ms=latency,
        )

    def stream(
        self, prompt: str, params: GenerationParams
    ) -> Iterator[StreamChunk]:
        """Stream text generation via Ollama."""
        import json
        import urllib.request
        import urllib.error

        url = f"{self.config.base_url}/api/generate"
        payload = {
            "model": self.config.model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": params.temperature,
                "top_p": params.top_p,
                "top_k": params.top_k,
                "num_predict": params.max_tokens,
                "repeat_penalty": params.repeat_penalty,
            },
        }
        if params.seed is not None:
            payload["options"]["seed"] = params.seed

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
            )
            resp = urllib.request.urlopen(req, timeout=self.config.timeout_seconds)
            for line in resp:
                if not line.strip():
                    continue
                chunk_data = json.loads(line.decode())
                done = chunk_data.get("done", False)
                text = chunk_data.get("response", "")
                usage = None
                if done:
                    usage = TokenUsage(
                        prompt_tokens=chunk_data.get("prompt_eval_count", 0),
                        completion_tokens=chunk_data.get("eval_count", 0),
                        total_tokens=(
                            chunk_data.get("prompt_eval_count", 0)
                            + chunk_data.get("eval_count", 0)
                        ),
                    )
                yield StreamChunk(text=text, done=done, usage=usage)
                if done:
                    break
            resp.close()
        except (urllib.error.URLError, OSError):
            yield StreamChunk(text="", done=True)

    def health_check(self) -> bool:
        """Check if Ollama is running."""
        import urllib.request
        import urllib.error

        try:
            req = urllib.request.Request(f"{self.config.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except (urllib.error.URLError, OSError):
            return False

    def list_models(self) -> List[str]:
        """List models available in Ollama."""
        import json
        import urllib.request
        import urllib.error

        try:
            req = urllib.request.Request(f"{self.config.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            return [m["name"] for m in data.get("models", [])]
        except (urllib.error.URLError, OSError, KeyError):
            return []


# =============================================================================
# Backend registry
# =============================================================================


_BACKEND_REGISTRY: Dict[ModelProvider, type] = {
    ModelProvider.OLLAMA: OllamaBackend,
}


def register_backend(
    provider: ModelProvider, backend_class: type
) -> None:
    """Register a custom backend class for a provider.

    Args:
        provider: The ModelProvider enum value.
        backend_class: A subclass of LocalModelBackend.
    """
    if not issubclass(backend_class, LocalModelBackend):
        raise TypeError("backend_class must subclass LocalModelBackend")
    _BACKEND_REGISTRY[provider] = backend_class


# =============================================================================
# Main client
# =============================================================================


class LocalModelClient:
    """Clean, type-safe interface for interacting with local models.

    Provides a unified API for text generation, chat, embeddings, and
    streaming across different local model providers. Integrates with
    MESIE spectral context for domain-specific intelligence.

    Args:
        config: Local model configuration.
        backend: Optional custom backend instance (overrides provider lookup).

    Example:
        >>> config = LocalModelConfig(provider=ModelProvider.OLLAMA, model_name="llama3")
        >>> client = LocalModelClient(config)
        >>> resp = client.generate("Explain resonance in structural dynamics")
        >>> print(resp.text)
    """

    def __init__(
        self,
        config: Optional[LocalModelConfig] = None,
        backend: Optional[LocalModelBackend] = None,
    ) -> None:
        self.config = config or LocalModelConfig()
        if backend is not None:
            self._backend = backend
        else:
            backend_cls = _BACKEND_REGISTRY.get(self.config.provider)
            if backend_cls is None:
                raise ValueError(
                    f"No backend registered for provider {self.config.provider.value}. "
                    f"Use register_backend() to add one, or pass a custom backend instance."
                )
            self._backend = backend_cls(self.config)

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None,
        seed: Optional[int] = None,
        spectral_context: Optional[SpectralContext] = None,
        params: Optional[GenerationParams] = None,
    ) -> GenerationResponse:
        """Generate text from a prompt.

        Args:
            prompt: The input prompt.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            top_p: Nucleus sampling threshold.
            stop: Stop sequences.
            seed: Random seed for reproducibility.
            spectral_context: Optional MESIE spectral context to prepend.
            params: Full GenerationParams (overrides individual args if given).

        Returns:
            A GenerationResponse with the generated text and metadata.
        """
        if params is None:
            params = GenerationParams(
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stop_sequences=stop or [],
                seed=seed,
            )

        full_prompt = prompt
        if spectral_context is not None:
            full_prompt = spectral_context.to_prompt_context() + "\n\n" + prompt

        return self._backend.generate(full_prompt, params)

    def chat(
        self,
        messages: List[ChatMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        spectral_context: Optional[SpectralContext] = None,
        params: Optional[GenerationParams] = None,
    ) -> GenerationResponse:
        """Chat-style completion from a list of messages.

        Args:
            messages: Conversation messages.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            spectral_context: Optional spectral context injected as system message.
            params: Full GenerationParams (overrides individual args if given).

        Returns:
            A GenerationResponse with the assistant's reply.
        """
        if params is None:
            params = GenerationParams(temperature=temperature, max_tokens=max_tokens)

        final_messages = list(messages)
        if spectral_context is not None:
            ctx_msg = ChatMessage.system(spectral_context.to_prompt_context())
            final_messages.insert(0, ctx_msg)

        return self._backend.chat(final_messages, params)

    def embed(self, text: str) -> EmbeddingResponse:
        """Compute an embedding vector for the given text.

        Args:
            text: Input text to embed.

        Returns:
            An EmbeddingResponse with the embedding vector.
        """
        return self._backend.embed(text)

    def stream(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        spectral_context: Optional[SpectralContext] = None,
        params: Optional[GenerationParams] = None,
    ) -> Iterator[StreamChunk]:
        """Stream text generation chunk by chunk.

        Args:
            prompt: The input prompt.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            spectral_context: Optional MESIE spectral context.
            params: Full GenerationParams.

        Yields:
            StreamChunk objects with incremental text.
        """
        if params is None:
            params = GenerationParams(temperature=temperature, max_tokens=max_tokens)

        full_prompt = prompt
        if spectral_context is not None:
            full_prompt = spectral_context.to_prompt_context() + "\n\n" + prompt

        yield from self._backend.stream(full_prompt, params)

    # ------------------------------------------------------------------
    # MESIE spectral integration helpers
    # ------------------------------------------------------------------

    def analyze_spectrum(
        self,
        spectral_context: SpectralContext,
        question: str = "Analyze this spectral pattern and describe its characteristics.",
        *,
        temperature: float = 0.4,
        max_tokens: int = 2048,
    ) -> GenerationResponse:
        """Ask the local model to analyze spectral data described by the context.

        Convenience method that combines spectral context injection with
        a domain-specific analysis prompt.

        Args:
            spectral_context: MESIE spectral context describing the data.
            question: The analysis question to ask.
            temperature: Lower temperature for factual analysis.
            max_tokens: Maximum response length.

        Returns:
            GenerationResponse with the model's spectral analysis.
        """
        system = ChatMessage.system(
            "You are a spectral intelligence analyst integrated with the MESIE "
            "(Multi-Element Spectral Intelligence Engine) framework. Provide "
            "precise, technical analysis of spectral data."
        )
        context = ChatMessage.system(spectral_context.to_prompt_context())
        user = ChatMessage.user(question)

        params = GenerationParams(temperature=temperature, max_tokens=max_tokens)
        return self._backend.chat([system, context, user], params)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def health_check(self) -> bool:
        """Check whether the local model backend is reachable."""
        return self._backend.health_check()

    def list_models(self) -> List[str]:
        """List available models on the backend."""
        return self._backend.list_models()

    @property
    def provider(self) -> ModelProvider:
        """The active provider."""
        return self.config.provider

    @property
    def model_name(self) -> str:
        """The active model name."""
        return self.config.model_name

    def __repr__(self) -> str:
        return (
            f"LocalModelClient(provider={self.config.provider.value!r}, "
            f"model={self.config.model_name!r})"
        )

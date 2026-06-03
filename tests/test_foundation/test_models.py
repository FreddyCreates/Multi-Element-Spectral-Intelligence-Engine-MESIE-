"""Tests for model architectures."""

import numpy as np
import pytest

from mesie.foundation.models.positional_encoding import (
    RotaryEmbedding,
    FrequencyAwarePositionalEncoding,
    SpectralHarmonicEncoding,
    ALiBiEncoding,
    SpectralPositionalEncoding,
)
from mesie.foundation.models.transformer_blocks import (
    RMSNorm,
    SpectralMultiHeadAttention,
    SpectralFeedForward,
    SpectralTransformerBlock,
)
from mesie.foundation.models.spectral_encoder import (
    LearnableDFTLayer,
    WaveletDecompositionLayer,
    HarmonicAttentionLayer,
    OctaveBandPooling,
    SpectralInputEncoder,
)
from mesie.foundation.models.mixture_of_experts import (
    ExpertLayer,
    ModalityAwareRouter,
    MixtureOfExperts,
)
from mesie.foundation.models.output_heads import (
    SpectralReconstructionHead,
    NextWindowPredictionHead,
    ContrastiveProjectionHead,
    ClassificationHead,
)
from mesie.foundation.models.spectral_gpt import SpectralGPT


class TestPositionalEncoding:
    """Tests for positional encoding variants."""

    def test_rotary_shape(self):
        """Rotary encoding should preserve shape."""
        pe = RotaryPositionalEncoding(dim=64, max_seq_len=512)
        x = np.random.randn(2, 128, 64)
        out = pe.forward(x)
        assert out.shape == x.shape

    def test_frequency_aware_shape(self):
        """Frequency-aware encoding should produce correct shape."""
        pe = FrequencyAwarePositionalEncoding(dim=64, max_seq_len=512)
        x = np.random.randn(2, 128, 64)
        out = pe.forward(x)
        assert out.shape == x.shape

    def test_harmonic_shape(self):
        """Harmonic encoding should produce correct shape."""
        pe = HarmonicPositionalEncoding(dim=64, max_seq_len=512)
        x = np.random.randn(2, 128, 64)
        out = pe.forward(x)
        assert out.shape == x.shape

    def test_alibi_shape(self):
        """ALiBi should produce correct bias shape."""
        pe = ALiBiPositionalEncoding(num_heads=8, max_seq_len=512)
        bias = pe.get_bias(128)
        assert bias.shape == (8, 128, 128)


class TestRMSNorm:
    """Tests for RMS normalization."""

    def test_output_shape(self):
        norm = RMSNorm(dim=64)
        x = np.random.randn(2, 32, 64)
        out = norm.forward(x)
        assert out.shape == x.shape

    def test_normalization(self):
        """RMS of output should be approximately 1."""
        norm = RMSNorm(dim=64)
        x = np.random.randn(2, 32, 64) * 5
        out = norm.forward(x)
        rms = np.sqrt(np.mean(out ** 2, axis=-1))
        assert np.allclose(rms, 1.0, atol=0.2)


class TestMultiHeadAttention:
    """Tests for spectral multi-head attention."""

    def test_output_shape(self):
        attn = SpectralMultiHeadAttention(dim=64, num_heads=8)
        x = np.random.randn(2, 32, 64)
        out = attn.forward(x)
        assert out.shape == x.shape

    def test_different_seq_lengths(self):
        attn = SpectralMultiHeadAttention(dim=64, num_heads=8)
        for seq_len in [16, 32, 64, 128]:
            x = np.random.randn(1, seq_len, 64)
            out = attn.forward(x)
            assert out.shape == (1, seq_len, 64)


class TestSpectralFeedForward:
    """Tests for spectral feed-forward network."""

    def test_output_shape(self):
        ffn = SpectralFeedForward(dim=64, hidden_dim=256)
        x = np.random.randn(2, 32, 64)
        out = ffn.forward(x)
        assert out.shape == x.shape


class TestTransformerBlock:
    """Tests for full transformer block."""

    def test_output_shape(self):
        block = SpectralTransformerBlock(dim=64, num_heads=8, ff_dim=256)
        x = np.random.randn(2, 32, 64)
        out = block.forward(x)
        assert out.shape == x.shape


class TestSpectralEncoder:
    """Tests for spectral input encoder."""

    def test_learnable_dft(self):
        dft = LearnableDFTLayer(input_dim=128, output_dim=64)
        x = np.random.randn(2, 128)
        out = dft.forward(x)
        assert out.shape == (2, 64)

    def test_wavelet_decomposition(self):
        wavelet = WaveletDecompositionLayer(input_dim=128, num_scales=4)
        x = np.random.randn(2, 128)
        out = wavelet.forward(x)
        assert out.shape[0] == 2

    def test_harmonic_attention(self):
        harm = HarmonicAttentionLayer(dim=64, num_harmonics=8)
        x = np.random.randn(2, 32, 64)
        out = harm.forward(x)
        assert out.shape == x.shape

    def test_octave_pooling(self):
        pool = OctaveBandPooling(input_dim=128, num_octaves=8)
        x = np.random.randn(2, 128)
        out = pool.forward(x)
        assert out.shape[0] == 2

    def test_full_encoder(self):
        encoder = SpectralInputEncoder(
            input_dim=256, output_dim=128, sample_rate=1000.0
        )
        x = np.random.randn(2, 256)
        out = encoder.forward(x)
        assert out.shape == (2, 128)


class TestMixtureOfExperts:
    """Tests for MoE module."""

    def test_expert_output_shape(self):
        expert = SpectralExpert(input_dim=64, hidden_dim=256, output_dim=64)
        x = np.random.randn(2, 32, 64)
        out = expert.forward(x)
        assert out.shape == x.shape

    def test_router_output(self):
        router = ModalityAwareRouter(
            input_dim=64, num_experts=4, num_modalities=7
        )
        x = np.random.randn(2, 32, 64)
        weights, indices = router.forward(x)
        assert weights.shape[0] == 2 * 32
        assert indices.shape[0] == 2 * 32

    def test_moe_output_shape(self):
        moe = SpectralMixtureOfExperts(
            input_dim=64, hidden_dim=256, num_experts=4
        )
        x = np.random.randn(2, 32, 64)
        out = moe.forward(x)
        assert out.shape == x.shape


class TestOutputHeads:
    """Tests for output heads."""

    def test_reconstruction_head(self):
        head = ReconstructionHead(input_dim=64, output_dim=128)
        x = np.random.randn(2, 32, 64)
        out = head.forward(x)
        assert out.shape == (2, 32, 128)

    def test_next_window_head(self):
        head = NextWindowHead(input_dim=64, output_dim=128)
        x = np.random.randn(2, 32, 64)
        out = head.forward(x)
        assert out.shape[0] == 2

    def test_contrastive_head(self):
        head = ContrastiveHead(input_dim=64, projection_dim=32)
        x = np.random.randn(2, 32, 64)
        out = head.forward(x)
        assert out.shape == (2, 32)

    def test_classification_head(self):
        head = ClassificationHead(input_dim=64, num_classes=10)
        x = np.random.randn(2, 32, 64)
        out = head.forward(x)
        assert out.shape == (2, 10)


class TestSpectralGPT:
    """Tests for the main SpectralGPT model."""

    def test_creation(self):
        model = SpectralGPT(
            vocab_size=1024,
            hidden_dim=64,
            num_layers=2,
            num_heads=4,
            max_seq_len=256,
        )
        assert model is not None

    def test_forward_discrete(self):
        model = SpectralGPT(
            vocab_size=1024,
            hidden_dim=64,
            num_layers=2,
            num_heads=4,
            max_seq_len=256,
        )
        tokens = np.random.randint(0, 1024, (2, 32))
        output = model.forward(tokens, input_type="discrete")
        assert "hidden_states" in output
        assert output["hidden_states"].shape == (2, 32, 64)

    def test_forward_continuous(self):
        model = SpectralGPT(
            vocab_size=1024,
            hidden_dim=64,
            num_layers=2,
            num_heads=4,
            max_seq_len=256,
            input_dim=128,
        )
        x = np.random.randn(2, 32, 128)
        output = model.forward(x, input_type="continuous")
        assert "hidden_states" in output

    def test_get_embeddings(self):
        model = SpectralGPT(
            vocab_size=1024,
            hidden_dim=64,
            num_layers=2,
            num_heads=4,
            max_seq_len=256,
            input_dim=128,
        )
        x = np.random.randn(2, 32, 128)
        emb = model.get_embeddings(x, input_type="continuous")
        assert emb.shape[0] == 2
        assert emb.shape[-1] == 64

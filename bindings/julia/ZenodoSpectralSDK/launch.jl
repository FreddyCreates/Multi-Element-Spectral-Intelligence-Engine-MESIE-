#!/usr/bin/env julia
"""
MESIE ZenodoSpectralSDK — One-Shot Launcher

Run this single file to automatically:
1. Install all required Julia dependencies
2. Activate the SDK environment
3. Launch the interactive Research OS terminal

Usage:
    julia launch.jl

That's it. Everything else is handled automatically.
"""

println()
println("╔══════════════════════════════════════════════════════════════════╗")
println("║   MESIE — Multi-Element Spectral Intelligence Engine            ║")
println("║   ZenodoSpectralSDK Research OS                                 ║")
println("║   v0.1.0                                                        ║")
println("╚══════════════════════════════════════════════════════════════════╝")
println()

# --- Step 1: Auto-install dependencies ---
println("⏳ Initializing environment...")

import Pkg

# Activate the project
project_dir = @__DIR__
Pkg.activate(project_dir)

# Install all dependencies automatically
println("📦 Installing dependencies (first run may take a minute)...")
try
    Pkg.instantiate()
    Pkg.resolve()
catch e
    println("⚠️  Dependency resolution needed, adding packages...")
    Pkg.add([
        Pkg.PackageSpec(name="HTTP"),
        Pkg.PackageSpec(name="JSON"),
        Pkg.PackageSpec(name="Downloads"),
    ])
    Pkg.resolve()
    Pkg.instantiate()
end

println("✅ All dependencies installed.")
println()

# --- Step 2: Load the SDK ---
println("🔬 Loading ZenodoSpectralSDK modules...")
include(joinpath(project_dir, "src", "ZenodoSpectralSDK.jl"))
using .ZenodoSpectralSDK

println("✅ SDK loaded successfully.")
println()

# --- Step 3: Launch interactive REPL ---
include(joinpath(project_dir, "src", "repl.jl"))
launch_research_os()

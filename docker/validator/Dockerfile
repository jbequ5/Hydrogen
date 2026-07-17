# hydrogen/validator:pino-v0.2 (Improved Phase 0)
# Pinned, reproducible, and more robust validator image

FROM nvcr.io/nvidia/pytorch:24.09-py3 AS builder

LABEL maintainer="Hydrogen contributors <jbequ5>"
LABEL description="Hydrogen validator image with PhysicsNeMo (improved)"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates julia=1.10.* \
    && rm -rf /var/lib/apt/lists/*

# Install Julia packages (for symbolic metadata)
RUN julia -e 'using Pkg; Pkg.add(["ModelingToolkit", "Symbolics", "DataDrivenDiffEq"]); Pkg.precompile()'

# Install Python dependencies with pinned versions where possible
RUN pip install --no-cache-dir \
    "physicsnemo==1.0.0" \
    "neuraloperator>=0.3.0" \
    "bittensor>=6.0" \
    "torch>=2.3" \
    "numpy" "scipy" "pandas" "pyyaml" "tqdm" "juliacall" "python-dotenv"

# Final runtime image (smaller)
FROM nvcr.io/nvidia/pytorch:24.09-py3

COPY --from=builder /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /root/.julia /root/.julia

WORKDIR /workspace

# Copy Hydrogen code
COPY . /workspace/hydrogen

# Healthcheck
HEALTHCHECK --interval=30s --timeout=15s --start-period=10s --retries=3 \
    CMD python -c "import torch, physicsnemo; print('CUDA:', torch.cuda.is_available()); print('PhysicsNeMo OK')" || exit 1

# Default entrypoint (can be overridden)
ENTRYPOINT ["python", "-m", "hydrogen.validator.entrypoint"]

FROM mambaorg/micromamba:1.5.10

WORKDIR /workspace

COPY . /workspace

RUN micromamba install -y -n base -f environment.benchmark.yml \
    && micromamba clean --all --yes

ENTRYPOINT ["micromamba", "run", "-n", "base", "python", "scripts/build_full_evidence_package.py"]
CMD ["--output-dir", "results", "--execute-api", "--run-external"]

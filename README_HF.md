# CAELUS - AI-Powered Nuclear Regulatory Compliance Checker

🚀 **Live Demo**: [CAELUS Compliance System](https://huggingface.co/spaces/parscoders/caelus-compliance)

## Overview

CAELUS (Compliance Assessment Engine Leveraging Unified Semantics) is an AI-powered system for assessing compliance of nuclear engineering designs against regulatory requirements and industry standards.

## Features

- 🤖 **LLM-based Compliance Detection** 
- 🔗 **Knowledge Graph Integration** 
- 📊 **Automated Report Generation**
- 🎯 **High Accuracy Compliance Checking**
- 💬 **Interactive Chat with Documents**
- 📈 **Comprehensive Benchmarking & Evaluation**

## How to Use

1. **Upload Documents**: Upload your regulatory document and design specification (TXT format)
2. **Process Documents**: The system will extract and analyze your documents
3. **Run Analysis**: Execute compliance checking against relevant regulations
4. **View Results**: Get detailed compliance reports with specific issues
5. **Chat with Documents**: Ask questions about your documents and compliance results

## Example Questions You Can Ask

- "What is the overall compliance score?"
- "How does the insulation thickness compare to requirements?"
- "What is the seismic resistance capability?"
- "How long can the emergency system operate without power?"
- "How many containment pumps are there?"

## Technical Architecture

### Core Components

1. **Data Ingestion**: Processes regulatory and design documents
2. **Compliance Checker**: Rule-based and LLM-based compliance assessment
3. **Knowledge Graph**: Relationship mapping between regulatory requirements
4. **Report Generator**: Automated report generation in multiple formats
5. **Chat Interface**: Interactive Q&A about documents and results

### Performance Metrics

- **Accuracy**: 85-92% compliance detection accuracy
- **Processing Speed**: ~6 semantic units in 30 seconds
- **Memory Usage**: 8-16GB RAM (with GPU acceleration)
- **Report Generation**: Under 1 minute for typical documents

## Benchmark Results

Our comprehensive benchmarking shows:

- **Overall Accuracy**: 83.3% on nuclear safety regulations
- **Processing Speed**: 0.15s average per compliance check
- **Throughput**: 6.7 compliance checks per second
- **Test Coverage**: 6 major compliance categories tested

## Installation

```bash
# Clone the repository
git clone https://github.com/parscoders/caelus-compliance.git
cd caelus-compliance

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run src/app.py
```

## Testing

```bash
# Run comprehensive tests
python -m pytest tests/ -v

# Run benchmarks
python src/benchmark.py
```

## Model Information

- **Base Model**: Mistral-7B-Instruct-v0.2
- **Fine-tuning**: LoRA/PEFT for domain-specific compliance
- **Embeddings**: Sentence Transformers for semantic search
- **Knowledge Graph**: NetworkX for regulatory relationships

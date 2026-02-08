# AI Models & Benchmarks Guide

## Available AI Models
The system supports multiple AI models for quality assurance:

| Model | Use Case | Performance |
|-------|----------|-------------|
| **GPT-5** | Primary model for most validations | High accuracy, moderate speed |
| **GPT-4/4o** | Alternative model when GPT-5 is not available | Good accuracy, reliable |
| **Custom SFDR Prompts** | Specialized prompts sent to the AI models for sustainability reporting | Optimized for SFDR regulations |sustainability data |

## Running Experiments & Benchmarks

1. **Start Jupyter:**
   ```bash
   pdm run jupyter-lab
   # or
   pdm run jupyter-notebook
   ```
Then navigate to the `notebooks/` directory.



### Using the Dashboard
For production benchmarking:
1. Use the **Monitor Dashboard** to configure experiments
2. Run parallel tests with different AI models
3. Export results for comparative analysis

## SFDR Prompts
Specialized prompts for Sustainable Finance Disclosure Regulation (SFDR) are stored in: `src/dataland_qa_lab/prompts/sfdr.json`


The JSON file contains named prompt entries for different validation scenarios.

### To update SFDR prompts:  
1. Open and edit the `src/dataland_qa_lab/prompts/sfdr.json` file  
2. Add or modify prompt entries in the JSON structure, keeping valid JSON and following existing naming convention


## Best Practices

### Model Selection Guide
- **Use GPT-5** for:
  - Most production validations
  - High-stakes compliance checks
  
- **Use GPT-4/4o** for:
  - When GPT-5 is not available
  - Development and testing

- **Use SFDR prompts** for:
  - Sustainability reporting validations (prompts are sent to the selected AI model)

## Troubleshooting
- **No benchmark script found:** Use the provided Jupyter notebooks instead
- **Script not working:** Ensure all dependencies are installed with `pdm install`
- **Questions about benchmarks:** Contact project maintainers

*Last Updated: February 2025*
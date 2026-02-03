# AI Models & Benchmarks Guide

## Available AI Models
The system supports multiple AI models for quality assurance:

| Model | Use Case | Performance |
|-------|----------|-------------|
| **GPT-4 Turbo** | Primary model for most validations | High accuracy, moderate speed |
| **GPT-3.5 Turbo** | Faster validations where high accuracy is less critical | Lower accuracy, faster speed |
| **Custom SFDR Prompts** | Specialized for Sustainable Finance Disclosure Regulation reporting | Optimized for sustainability data |

## Running Experiments & Benchmarks

1. **Start Jupyter:**
   ```bash
   pdm run jupyter-lab
   # or
   pdm run jupyter-notebook
   ```
Then navigate to the `notebooks/` directory.

2. **Available Notebooks:**
   - `project_demo.ipynb` - Comprehensive demo of AI validation capabilities
   - `test_existing_company_reports.ipynb` - Test suite for company report validations
   - `base.ipynb` - Foundation for custom experiments

### Using the Dashboard
For production benchmarking:
1. Use the **Monitor Dashboard** to configure experiments
2. Run parallel tests with different AI models
3. Export results for comparative analysis

## SFDR Prompts
Specialized prompts for Sustainable Finance Disclosure Regulation (SFDR) are stored in: src/dataland_qa_lab/prompts/sfdr/

- `sfdr_data_validation.txt` - General SFDR data validation
- `sfdr_report_check.txt` - SFDR report compliance checking
- Additional specialized prompts as needed

### To update SFDR prompts:
1. Edit the `.txt` files in the prompts directory
2. Follow existing naming conventions
3. The system automatically loads updated prompts on restart

## Best Practices

### Model Selection Guide
- **Use GPT-4 Turbo** for:
  - Critical business validations
  - Complex logical reasoning
  - High-stakes compliance checks
  
- **Use GPT-3.5 Turbo** for:
  - Development and testing
  - Simple format validations
  - High-volume, low-risk checks
  
- **Use SFDR prompts** for:
  - Sustainability reporting validations
  - ESG (Environmental, Social, Governance) compliance
  - Regulatory reporting checks

## Troubleshooting
- **No benchmark script found:** Use the provided Jupyter notebooks instead
- **Script not working:** Ensure all dependencies are installed with `pdm install`
- **Questions about benchmarks:** Contact project maintainers

*Last Updated: February 2025*
# Data Frameworks and Data Access

This document explains how to find and access various sustainability data frameworks on the Dataland platform, including SFDR data.

## Supported Frameworks on Dataland

The Dataland platform provides access to multiple sustainability data frameworks:

### SFDR (Sustainable Finance Disclosure Regulation)

SFDR data can be accessed on the Dataland platform at:
- **Production**: [https://dataland.com/companies](https://dataland.com/companies)
- **Test Environment**: [https://test.dataland.com/companies](https://test.dataland.com/companies)

To find SFDR data for a specific company:
1. Navigate to the Dataland platform
2. Search for the company using the search bar
3. Select the company from the search results
4. Look for the "SFDR" framework in the company's available datasets

### EU Taxonomy Nuclear and Gas

EU Taxonomy Nuclear and Gas data is the primary focus of this QA Lab. This framework covers disclosures related to nuclear and gas activities under the EU Taxonomy Regulation.

Data can be accessed programmatically via the `eu_taxonomy_nuclear_and_gas_api` endpoint, as implemented in this codebase.

### EU Taxonomy Non-Financials

The EU Taxonomy Non-Financials framework covers taxonomy-related disclosures for non-financial companies.

## QA Lab Supported Frameworks

Currently, the Dataland QA Lab supports automated quality assurance for:

- **EU Taxonomy Nuclear and Gas** - Full support with automated review and report generation

Future expansion may include additional frameworks such as SFDR.

## Accessing Data via API

For programmatic access to data on Dataland, refer to the `DatalandClient` class in `src/dataland_qa_lab/dataland/dataland_client.py`. This client provides access to various Dataland APIs including:

- Company Data Controller API
- EU Taxonomy Nuclear and Gas Data Controller API
- EU Taxonomy Non-Financials Data Controller API
- QA Report Controller APIs

## Data Request Status

To check the status of pending data requests (datasets awaiting QA review), the QA Lab queries the Dataland QA API for datasets with `QaStatus.PENDING`. Currently, only "nuclear-and-gas" data types are processed automatically.

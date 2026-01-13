import asyncio
import io
import json
import logging

import async_lru
import pypdf
from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.data_point_flow import models, prompts
from dataland_qa_lab.utils import config

config = config.get_config()


logger = logging.getLogger(__name__)
validation_prompts = prompts.get_prompts()


@async_lru.alru_cache
async def get_data_point(data_point_id: str) -> models.DataPoint:
    """Returns a DataPoint object for the given data_point_id and also validates its structure."""
    logger.info("Fetching data point with ID: %s", data_point_id)
    data_point = await asyncio.to_thread(
        config.dataland_client.data_points_api.get_data_point, data_point_id=data_point_id
    )
    dp_json = json.loads(data_point.data_point)

    data_point_type = data_point.data_point_type
    if dp_json.get("dataSource") is None:
        msg = f"Data point {data_point_id} is missing dataSource information."
        raise ValueError(msg)
    page = int(dp_json["dataSource"].get("page", 0))
    file_reference = dp_json["dataSource"].get("fileReference", "")
    file_name = dp_json["dataSource"].get("fileName", "")
    value = dp_json.get("value", "")

    return models.DataPoint(
        data_point_id=data_point_id,
        data_point_type=data_point_type,
        data_source=dp_json.get("dataSource", {}),
        page=page,
        file_reference=file_reference,
        file_name=file_name,
        value=value,
    )


@async_lru.alru_cache
async def get_document(reference_id: str, page_num: int) -> io.BytesIO:
    """Return a PDF document stream for specific pages."""
    logger.info("Downloading document with reference ID: %s", reference_id)
    full_pdf = await asyncio.to_thread(config.dataland_client.documents_api.get_document, document_id=reference_id)
    full_pdf_stream = io.BytesIO(full_pdf)

    original_pdf = pypdf.PdfReader(full_pdf_stream)
    output_pdf = pypdf.PdfWriter()

    if 0 <= page_num - 1 < len(original_pdf.pages):
        output_pdf.add_page(original_pdf.pages[page_num - 1])

    extracted_pdf_stream = io.BytesIO()
    output_pdf.write(extracted_pdf_stream)
    extracted_pdf_stream.seek(0)

    return extracted_pdf_stream


async def override_dataland_qa(data_point_id: str, reasoning: str, qa_status: QaStatus) -> None:
    """Override Dataland QA status for the given data point ID."""
    logger.info("Overriding Dataland QA status for data point ID: %s to %s", data_point_id, qa_status)
    await asyncio.to_thread(
        config.dataland_client.qa_api.change_data_point_qa_status,
        data_point_id=data_point_id,
        qa_status=qa_status,
        comment=reasoning,
    )


async def get_dependency_values(data_point_id: str, dependency_field_names: list[str]) -> dict[str, str]:
    # Get values from SFDR dataset for fields we depend on
    if not dependency_field_names:
        return {}
    
    try:
        # Get info about the datapoint
        meta = await asyncio.to_thread(
            config.dataland_client.data_points_api.get_data_point_meta_info,
            data_point_id=data_point_id
        )
        
        # Find all datasets for this company and year
        datasets = await asyncio.to_thread(
            config.dataland_client.meta_api.get_list_of_data_meta_info,
            company_id=meta.company_id,
            reporting_period=meta.reporting_period,
            show_only_active=True
        )
        
        # Look for SFDR dataset
        sfdr_id = None
        for dataset in datasets:
            if "sfdr" in str(dataset.data_type).lower():
                sfdr_id = dataset.data_id
                break
        
        if not sfdr_id:
            return {name: "not available" for name in dependency_field_names}
        
        # Get SFDR data
        sfdr_data = await asyncio.to_thread(
            config.dataland_client.sfdr_api.get_company_associated_sfdr_data,
            data_id=sfdr_id
        )
        
        # Convert to dict to search through it
        data_dict = sfdr_data.data.model_dump()
        
        # Find the values we need
        results = {}
        for field_name in dependency_field_names:
            # For revenue, we know it's in environmental.greenhouse_gas_emissions.total_revenue_in_eur
            if field_name == 'extendedDecimalTotalRevenueInEUR':
                try:
                    value = data_dict['environmental']['greenhouse_gas_emissions']['total_revenue_in_eur']
                    results[field_name] = str(value) if value is not None else "not available"
                except (KeyError, TypeError):
                    results[field_name] = "not available"
            else:
                results[field_name] = "not available"
        
        return results
        
    except Exception:
        return {name: "not available" for name in dependency_field_names}

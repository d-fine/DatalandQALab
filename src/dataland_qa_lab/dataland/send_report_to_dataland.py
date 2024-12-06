from datetime import date

from dataland_qa import models as m
from dataland_qa.models.nuclear_and_gas_data import NuclearAndGasData
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict
from pydantic import BaseModel, StrictStr

from dataland_qa_lab.dataland.dataland_client import DatalandClient


class ReportData(BaseModel):  # noqa: D101
    commentqareportdatapointmapstringcompanyreport: StrictStr
    commentqareportdatapointextendeddatapointyesno: StrictStr
    commentextendeddatapointyesno: StrictStr
    verdictqareportdatapointmapstringcompanyreport: QaReportDataPointVerdict
    verdictqareportdatapointextendeddatapointyesno: QaReportDataPointVerdict
    corrected_data: dict[str, "CompanyReportData"]
    value: StrictStr
    quality: StrictStr
    data_source: "DocumentReferenceData"


class CompanyReportData(BaseModel):  # noqa: D101
    file_reference: StrictStr
    file_name: StrictStr | None
    publication_date: date | None


class DocumentReferenceData(BaseModel):  # noqa: D101
    file_reference: StrictStr | None
    page: StrictStr | None
    tag_name: StrictStr | None
    file_name: StrictStr | None


def create_qa_report(report_data: ReportData) -> NuclearAndGasData:
    """Sends a nuclear and gas QA report to the Dataland API."""
    selected_qa_report = NuclearAndGasData(
        general=m.NuclearAndGasGeneral(
            general=m.NuclearAndGasGeneralGeneral(
                referencedReports=m.QaReportDataPointMapStringCompanyReport(
                    comment=report_data.commentqareportdatapointmapstringcompanyreport,
                    verdict=report_data.verdictqareportdatapointmapstringcompanyreport,
                    correctedData={
                        key: m.CompanyReport(
                            file_reference=report.file_reference,
                            file_name=report.file_name,
                            publication_date=report.publication_date,
                        )
                        for key, report in report_data.corrected_data.items()
                    },
                ),
                nuclearEnergyRelatedActivitiesSection426=m.QaReportDataPointExtendedDataPointYesNo(
                    comment=report_data.commentqareportdatapointextendeddatapointyesno,
                    verdict=report_data.verdictqareportdatapointextendeddatapointyesno,
                    correctedData=m.ExtendedDataPointYesNo(
                        value=report_data.value,
                        quality=report_data.quality,
                        comment=report_data.commentextendeddatapointyesno,
                        dataSource=m.ExtendedDocumentReference(
                            fileReference=report_data.data_source.file_reference,
                            page=report_data.data_source.page,
                            tagName=report_data.data_source.tag_name,
                            fileName=report_data.data_source.file_name,
                        ),
                    ),
                ),
                nuclearEnergyRelatedActivitiesSection427=m.QaReportDataPointExtendedDataPointYesNo(
                    comment=report_data.commentqareportdatapointextendeddatapointyesno,
                    verdict=report_data.verdictqareportdatapointextendeddatapointyesno,
                    correctedData=m.ExtendedDataPointYesNo(
                        value=report_data.value,
                        quality=report_data.quality,
                        comment=report_data.commentextendeddatapointyesno,
                        dataSource=m.ExtendedDocumentReference(
                            fileReference=report_data.data_source.file_reference,
                            page=report_data.data_source.page,
                            tagName=report_data.data_source.tag_name,
                            fileName=report_data.data_source.file_name,
                        ),
                    ),
                ),
                nuclearEnergyRelatedActivitiesSection428=m.QaReportDataPointExtendedDataPointYesNo(
                    comment=report_data.commentqareportdatapointextendeddatapointyesno,
                    verdict=report_data.verdictqareportdatapointextendeddatapointyesno,
                    correctedData=m.ExtendedDataPointYesNo(
                        value=report_data.value,
                        quality=report_data.quality,
                        comment=report_data.commentextendeddatapointyesno,
                        dataSource=m.ExtendedDocumentReference(
                            fileReference=report_data.data_source.file_reference,
                            page=report_data.data_source.page,
                            tagName=report_data.data_source.tag_name,
                            fileName=report_data.data_source.file_name,
                        ),
                    ),
                ),
                fossilGasRelatedActivitiesSection429=m.QaReportDataPointExtendedDataPointYesNo(
                    comment=report_data.commentqareportdatapointextendeddatapointyesno,
                    verdict=report_data.verdictqareportdatapointextendeddatapointyesno,
                    correctedData=m.ExtendedDataPointYesNo(
                        value=report_data.value,
                        quality=report_data.quality,
                        comment=report_data.commentextendeddatapointyesno,
                        dataSource=m.ExtendedDocumentReference(
                            fileReference=report_data.data_source.file_reference,
                            page=report_data.data_source.page,
                            tagName=report_data.data_source.tag_name,
                            fileName=report_data.data_source.file_name,
                        ),
                    ),
                ),
                fossilGasRelatedActivitiesSection430=m.QaReportDataPointExtendedDataPointYesNo(
                    comment=report_data.commentqareportdatapointextendeddatapointyesno,
                    verdict=report_data.verdictqareportdatapointextendeddatapointyesno,
                    correctedData=m.ExtendedDataPointYesNo(
                        value=report_data.value,
                        quality=report_data.quality,
                        comment=report_data.commentextendeddatapointyesno,
                        dataSource=m.ExtendedDocumentReference(
                            fileReference=report_data.data_source.file_reference,
                            page=report_data.data_source.page,
                            tagName=report_data.data_source.tag_name,
                            fileName=report_data.data_source.file_name,
                        ),
                    ),
                ),
                fossilGasRelatedActivitiesSection431=m.QaReportDataPointExtendedDataPointYesNo(
                    comment=report_data.commentqareportdatapointextendeddatapointyesno,
                    verdict=report_data.verdictqareportdatapointextendeddatapointyesno,
                    correctedData=m.ExtendedDataPointYesNo(
                        value=report_data.value,
                        quality=report_data.quality,
                        comment=report_data.commentextendeddatapointyesno,
                        dataSource=m.ExtendedDocumentReference(
                            fileReference=report_data.data_source.file_reference,
                            page=report_data.data_source.page,
                            tagName=report_data.data_source.tag_name,
                            fileName=report_data.data_source.file_name,
                        ),
                    ),
                ),
                # NuclearAndGasGeneralTaxonomyAlignedRevenueDenominator = m.NuclearAndGasAlignedDenominator(
                #   comment = ""
                #    ,verdict = ""
                #    , correctedData = m.ExtendedDataPoint
                # )
            )
        )
    )
    return selected_qa_report


def send_report_to_dataland(data_id: StrictStr, qa_report: NuclearAndGasData, dataland_client: DatalandClient) -> None:
    """Send report to dataland."""
    dataland_client.eu_taxonomy_nuclear_gas_qa_api.post_nuclear_and_gas_data_qa_report(data_id, qa_report)

from dataland_qa_lab.dataland import company_data, data_extraction, prompt_schema, prompts, template_extractor


def test_prompt_engineering() -> None:
    ps = prompt_schema.PromptSchema()
    te = template_extractor.TemplateExtractor()
    prompt = prompts.Prompts()
    data = company_data.CompanyData()

    rows_6 = [1, 2, 3, 4, 5, 6]
    rows_8 = [1, 2, 3, 4, 5, 6, 7, 8]

    pdf_tmp = data.get_company_pdf()
    page_tmp = data.get_company_pages()
    pdf = pdf_tmp[1]
    page = page_tmp[1]

    result = []

    if page[0] is not None:
        result.append(
            te.extract_template(
                prompt.generate_prompt_for_template1(data_extraction.ectract_page(page[0], pdf)),
                ps.generate_schema_for_template1(),
                rows_6,
            )
        )

    if page[1] is not None:
        result.append(
            te.extract_template(
                prompt.generate_prompt_for_template2(data_extraction.ectract_page(page[1], pdf)),
                ps.generate_schema_for_rows(rows_8),
                rows_8,
            )
        )

    if page[2] is not None:
        result.append(
            te.extract_template(
                prompt.generate_prompt_for_template3(data_extraction.ectract_page(page[2], pdf)),
                ps.generate_schema_for_rows(rows_8),
                rows_8,
            )
        )

    if page[3] is not None:
        result.append(
            te.extract_template(
                prompt.generate_prompt_for_template4(data_extraction.ectract_page(page[3], pdf)),
                ps.generate_schema_for_rows(rows_8),
                rows_8,
            )
        )

    if page[4] is not None:
        result.append(
            te.extract_template(
                prompt.generate_prompt_for_template5(data_extraction.ectract_page(page[4], pdf)),
                ps.generate_schema_tmeplate5(rows_8),
                rows_8,
            )
        )

    assert len(result) == 5

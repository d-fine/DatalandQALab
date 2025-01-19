from openai.types.chat import ChatCompletionMessageToolCall
from openai.types.chat.chat_completion import (
            ChatCompletion,
            ChatCompletionMessage,
            Choice,
)
from openai.types.chat.chat_completion_message_tool_call import Function

E2E_AZURE_DOCUMENT_INTELLIGENCE_MOCK = "134"
E2E_AZURE_OPEN_AI_TEMPLATE_1 = ChatCompletion(
    id="test1",
    choices=[
        Choice(
            finish_reason="stop",
            index=0,
            message=ChatCompletionMessage(
                role="assistant",
                tool_calls=[
                    ChatCompletionMessageToolCall(
                        id="call_EEG3soMwEWVsq3HVX3MGCdcE",
                        function=Function(
                            arguments='{"1": "No", "2": "No", "3": "No", "4": "Yes", "5": "Yes", "6": "No"}',
                            name="requested_information_precisely_found_in_relevant_documents"
                        ),
                        type="function"
                    )
                ]
            ),
            content_filter_results={}
        )
    ],
    created=0,
    model="test",
    object="chat.completion"
)
E2E_AZURE_OPEN_AI_TEMPLATE_2_REVENUE = ChatCompletion(
    id="test2",
    choices=[
        Choice(
            finish_reason="stop",
            index=0,
            message=ChatCompletionMessage(
                role="assistant",
                tool_calls=[
                    ChatCompletionMessageToolCall(
                        id="call_EEG3soMwEWVsq3HVX3MGCdcE",
                        function=Function(
                            arguments="""{"answer_value_CCM+CCA%_row1":"-1","answer_value_CCM%_row1":"-1","answer_value_CCA%_row1":"-1","answ
                            er_value_CCM+CCA%_row2":"-1","answer_value_CCM%_row2":"-1","answer_value_CCA%_row2":"-1","answer_value_CCM+CCA%
                            _row3":"-1","answer_value_CCM%_row3":"-1","answer_value_CCA%_row3":"-1","answer_value_CCM+CCA%_row4":"-1","ans
                            wer_value_CCM%_row4":"-1","answer_value_CCA%_row4":"-1","answer_value_CCM+CCA%_row5":"-1","answer_value_CCM%_r
                            ow5":"-1","answer_value_CCA%_row5":"-1","answer_value_CCM+CCA%_row6":"-1","answer_value_CCM%_row6":"-1","answer_
                            value_CCA%_row6":"-1","answer_value_CCM+CCA%_row7":"17","answer_value_CCM%_row7":"17","answer_value_CCA%_row7"
                            :"-1","answer_value_CCM+CCA%_row8":"-1","answer_value_CCM%_row8":"-1","answer_value_CCA%_row8":"-1"}""",
                            name="requested_information_precisely_found_in_relevant_documents"
                        ),
                        type="function"
                    )
                ]
            ),
            content_filter_results={}
        )
    ],
    created=0,
    model="test",
    object="chat.completion"
)
E2E_AZURE_OPEN_AI_TEMPLATE_2_CAPEX = ChatCompletion(
    id="test2",
    choices=[
        Choice(
            finish_reason="stop",
            index=0,
            message=ChatCompletionMessage(
                role="assistant",
                tool_calls=[
                    ChatCompletionMessageToolCall(
                        id="call_EEG3soMwEWVsq3HVX3MGCdcE",
                        function=Function(
                            arguments="""{"answer_value_CCM+CCA%_row1":"-1","answer_value_CCM%_row1":"-1","answer_value_CCA%_row1
                            ":"-1","answer_value_CCM+CCA%_row2":"-1","answer_value_CCM%_row2":"-1","answer_value_CCA%_row2":"-1","a
                            nswer_value_CCM+CCA%_row3":"-1","answer_value_CCM%_row3":"-1","answer_value_CCA%_row3":"-1","answer_val
                            ue_CCM+CCA%_row4":"-1","answer_value_CCM%_row4":"-1","answer_value_CCA%_row4":"-1","answer_value_CCM+CCA
                            %_row5":"-1","answer_value_CCM%_row5":"-1","answer_value_CCA%_row5":"-1","answer_value_CCM+CCA%_row6":"-1","a
                            nswer_value_CCM%_row6":"-1","answer_value_CCA%_row6":"-1","answer_value_CCM+CCA%_row7":"17","answer_
                            value_CCM%_row7":"17","answer_value_CCA%_row7":"-1","answer_value_CCM+CCA%_row8":"-1","answer_value_CC
                            M%_row8":"-1","answer_value_CCA%_row8":"-1"}""",
                            name="requested_information_precisely_found_in_relevant_documents"
                        ),
                        type="function"
                    )
                ]
            ),
            content_filter_results={}
        )
    ],
    created=0,
    model="test",
    object="chat.completion"
)
E2E_AZURE_OPEN_AI_TEMPLATE_3_REVENUE = ChatCompletion(
    id="test3",
    choices=[
        Choice(
            finish_reason="stop",
            index=0,
            message=ChatCompletionMessage(
                role="assistant",
                tool_calls=[
                    ChatCompletionMessageToolCall(
                        id="call_EEG3soMwEWVsq3HVX3MGCdcE",
                        function=Function(
                            arguments="""{"answer_value_CCM+CCA%_row1":"-1","answer_value_CCM%_row1":"-1","answer_va
                            lue_CCA%_row1":"-1","answer_value_CCM+CCA%_row2":"-1","answer_value_CCM%_row2":"-1","answe
                            r_value_CCA%_row2":"-1","answer_value_CCM+CCA%_row3":"-1","answer_value_CCM%_row3":"-1","a
                            nswer_value_CCA%_row3":"-1","answer_value_CCM+CCA%_row4":"-1","answer_value_CCM%_row4":"-1","a
                            nswer_value_CCA%_row4":"-1","answer_value_CCM+CCA%_row5":"-1","answer_value_CCM%_row
                            5":"-1","answer_value_CCA%_row5":"-1","answer_value_CCM+CCA%_row6":"-1","answer_value_CC
                            M%_row6":"-1","answer_value_CCA%_row6":"-1","answer_value_CCM+CCA%_row7":"89","answer_valu
                            e_CCM%_row7":"89","answer_value_CCA%_row7":"-1","answer_value_CCM+CCA%_row8":"-1","answer_va
                            lue_CCM%_row8":"-1","answer_value_CCA%_row8":"-1"}""",
                            name="requested_information_precisely_found_in_relevant_documents"
                        ),
                        type="function"
                    )
                ]
            ),
            content_filter_results={}
        )
    ],
    created=0,
    model="test",
    object="chat.completion"
)
E2E_AZURE_OPEN_AI_TEMPLATE_3_CAPEX = ChatCompletion(
    id="test3",
    choices=[
        Choice(
            finish_reason="stop",
            index=0,
            message=ChatCompletionMessage(
                role="assistant",
                tool_calls=[
                    ChatCompletionMessageToolCall(
                        id="call_EEG3soMwEWVsq3HVX3MGCdcE",
                        function=Function(
                            arguments="""{"answer_value_CCM+CCA%_row1":"-1","answer_value_CCM%_row1":"-1","answer
                            _value_CCA%_row1":"-1","answer_value_CCM+CCA%_row2":"-1","answer_value_CCM%_row2":"-1","answ
                            er_value_CCA%_row2":"-1","answer_value_CCM+CCA%_row3":"-1","answer_value_CCM%_row3":"-1
                            ","answer_value_CCA%_row3":"-1","answer_value_CCM+CCA%_row4":"-1","answer_value_CCM%_r
                            ow4":"-1","answer_value_CCA%_row4":"-1","answer_value_CCM+CCA%_row5":"-1","answer_value_CC
                            M%_row5":"-1","answer_value_CCA%_row5":"-1","answer_value_CCM+CCA%_row6":"-1","answer_val
                            ue_CCM%_row6":"-1","answer_value_CCA%_row6":"-1","answer_value_CCM+CCA%_row7":"89","answ
                            er_value_CCM%_row7":"89","answer_value_CCA%_row7":"-1","answer_value_CCM+CCA%_row8":"-1","
                            answer_value_CCM%_row8":"-1","answer_value_CCA%_row8":"-1"}""",
                            name="requested_information_precisely_found_in_relevant_documents"
                        ),
                        type="function"
                    )
                ]
            ),
            content_filter_results={}
        )
    ],
    created=0,
    model="test",
    object="chat.completion"
)
E2E_AZURE_OPEN_AI_TEMPLATE_4_REVENUE = ChatCompletion(
    id="test4",
    choices=[
        Choice(
            finish_reason="stop",
            index=0,
            message=ChatCompletionMessage(
                role="assistant",
                tool_calls=[
                    ChatCompletionMessageToolCall(
                        id="call_EEG3soMwEWVsq3HVX3MGCdcE",
                        function=Function(
                            arguments="""{"answer_value_CCM+CCA%_row1": "-1", "answer_value_CCM%_row1": "-1", "answer_va
                            lue_CCA%_row1": "-1", "answer_value_CCM+CCA%_row2": "-1", "answer_value_CCM%_row2": "-1
                            ", "answer_value_CCA%_row2": "-1", "answer_value_CCM+CCA%_row3": "-1", "answer_value_C
                            CM%_row3": "-1", "answer_value_CCA%_row3": "-1", "answer_value_CCM+CCA%_row4": "-1", "a
                            nswer_value_CCM%_row4": "-1", "answer_value_CCA%_row4": "-1", "answer_value_CCM+CCA%_ro
                            w5": "-1", "answer_value_CCM%_row5": "-1", "answer_value_CCA%_row5": "-1", "answer_value_
                            CCM+CCA%_row6": "-1", "answer_value_CCM%_row6": "-1", "answer_value_CCA%_row6": "-1", "an
                            swer_value_CCM+CCA%_row7": "100", "answer_value_CCM%_row7": "100", "answer_value_CCA%_row
                            7": "-1", "answer_value_CCM+CCA%_row8": "100", "answer_value_CCM%_row8": "-1", "answer_v
                            alue_CCA%_row8": "-1"}""",
                            name="requested_information_precisely_found_in_relevant_documents"
                        ),
                        type="function"
                    )
                ]
            ),
            content_filter_results={}
        )
    ],
    created=0,
    model="test",
    object="chat.completion"
)
E2E_AZURE_OPEN_AI_TEMPLATE_4_CAPEX = ChatCompletion(
    id="test4",
    choices=[
        Choice(
            finish_reason="stop",
            index=0,
            message=ChatCompletionMessage(
                role="assistant",
                tool_calls=[
                    ChatCompletionMessageToolCall(
                        id="call_EEG3soMwEWVsq3HVX3MGCdcE",
                        function=Function(
                            arguments="""{"answer_value_CCM+CCA%_row1": "-1", "answer_value_CCM%_row1": "-1", "answer
                            _value_CCA%_row1": "-1", "answer_value_CCM+CCA%_row2": "-1", "answer_value_CCM%_row2": "
                            -1", "answer_value_CCA%_row2": "-1", "answer_value_CCM+CCA%_row3": "-1", "answer_value_C
                            CM%_row3": "-1", "answer_value_CCA%_row3": "-1", "answer_value_CCM+CCA%_row4": "-1", "ans
                            wer_value_CCM%_row4": "-1", "answer_value_CCA%_row4": "-1", "answer_value_CCM+CCA%_row5"
                            : "-1", "answer_value_CCM%_row5": "-1", "answer_value_CCA%_row5": "-1", "answer_value_C
                            CM+CCA%_row6": "-1", "answer_value_CCM%_row6": "-1", "answer_value_CCA%_row6": "-1", "an
                            swer_value_CCM+CCA%_row7": "100", "answer_value_CCM%_row7": "100", "answer_value_CCA%_ro
                            w7": "-1", "answer_value_CCM+CCA%_row8": "100", "answer_value_CCM%_row8": "-1", "answer_va
                            lue_CCA%_row8": "-1"}""",
                            name="requested_information_precisely_found_in_relevant_documents"
                        ),
                        type="function"
                    )
                ]
            ),
            content_filter_results={}
        )
    ],
    created=0,
    model="test",
    object="chat.completion"
)
E2E_AZURE_OPEN_AI_TEMPLATE_5_REVENUE = ChatCompletion(
    id="test5",
    choices=[
        Choice(
            finish_reason="stop",
            index=0,
            message=ChatCompletionMessage(
                role="assistant",
                tool_calls=[
                    ChatCompletionMessageToolCall(
                        id="call_EEG3soMwEWVsq3HVX3MGCdcE",
                        function=Function(
                            arguments="""{"answer_value_CCM+CCA%_row1": "-1", "answer_value_CCM%_row1": "-1", "answer_
                            value_CCA%_row1": "-1", "answer_value_CCM+CCA%_row2": "-1", "answer_value_CCM%_row2": "-1"
                            , "answer_value_CCA%_row2": "-1", "answer_value_CCM+CCA%_row3": "-1", "answer_value_CCM%_row
                            3": "-1", "answer_value_CCA%_row3": "-1", "answer_value_CCM+CCA%_row4": "-1", "answer_val
                            ue_CCM%_row4": "-1", "answer_value_CCA%_row4": "-1", "answer_value_CCM+CCA%_row5": "-1", "
                            answer_value_CCM%_row5": "-1", "answer_value_CCA%_row5": "-1", "answer_value_CCM+CCA%_row6"
                            : "-1", "answer_value_CCM%_row6": "-1", "answer_value_CCA%_row6": "-1", "answer_value_CCM+C
                            CA%_row7": "100", "answer_value_CCM%_row7": "100", "answer_value_CCA%_row7": "-1", "answe
                            r_value_CCM+CCA%_row8": "100", "answer_value_CCM%_row8": "-1", "answer_value_CCA%_row8": "
                            -1"}""",
                            name="requested_information_precisely_found_in_relevant_documents"
                        ),
                        type="function"
                    )
                ]
            ),
            content_filter_results={}
        )
    ],
    created=0,
    model="test",
    object="chat.completion"
)
E2E_AZURE_OPEN_AI_TEMPLATE_5_CAPEX = ChatCompletion(
    id="test5",
    choices=[
        Choice(
            finish_reason="stop",
            index=0,
            message=ChatCompletionMessage(
                role="assistant",
                tool_calls=[
                    ChatCompletionMessageToolCall(
                        id="call_EEG3soMwEWVsq3HVX3MGCdcE",
                        function=Function(
                            arguments="""{"answer_value_CCM+CCA%_row1": "-1", "answer_value_CCM%_row1": "-1", "answer_
                            value_CCA%_row1": "-1", "answer_value_CCM+CCA%_row2": "-1", "answer_value_CCM%_row2": "-1"
                            , "answer_value_CCA%_row2": "-1", "answer_value_CCM+CCA%_row3": "-1", "answer_value_CCM%_row
                            3": "-1", "answer_value_CCA%_row3": "-1", "answer_value_CCM+CCA%_row4": "-1", "answer_val
                            ue_CCM%_row4": "-1", "answer_value_CCA%_row4": "-1", "answer_value_CCM+CCA%_row5": "-1", "
                            answer_value_CCM%_row5": "-1", "answer_value_CCA%_row5": "-1", "answer_value_CCM+CCA%_row6"
                            : "-1", "answer_value_CCM%_row6": "-1", "answer_value_CCA%_row6": "-1", "answer_value_CCM+C
                            CA%_row7": "100", "answer_value_CCM%_row7": "100", "answer_value_CCA%_row7": "-1", "answe
                            r_value_CCM+CCA%_row8": "100", "answer_value_CCM%_row8": "-1", "answer_value_CCA%_row8": "
                            -1"}""",
                            name="requested_information_precisely_found_in_relevant_documents"
                        ),
                        type="function"
                    )
                ]
            ),
            content_filter_results={}
        )
    ],
    created=0,
    model="test",
    object="chat.completion"
)


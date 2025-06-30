import json

from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from pprint import pprint

from semantic_kernel.functions import kernel_function

from base_plugin import BasePlugin

class PresidioPlugin(BasePlugin):

    def __init__(self):
        super().__init__()

        self.anonymizer = AnonymizerEngine()
        self.analyzer = AnalyzerEngine()

    @kernel_function(
        name="anonymize_text",
        description="Used to anonymize sensitive information in text.",
    )
    def anonymize_text(self, text_to_anonymize: str) -> str:

        analyzer_results = self.analyzer.analyze(text=text_to_anonymize, entities=["PHONE_NUMBER"], language='en')

        anonymized_results = self.anonymizer.anonymize(
            text=text_to_anonymize,
            analyzer_results=analyzer_results,    
            operators={"DEFAULT": OperatorConfig("replace", {"new_value": "<ANONYMIZED>"}), 
                                "PHONE_NUMBER": OperatorConfig("mask", {"type": "mask", "masking_char" : "*", "chars_to_mask" : 12, "from_end" : True}),
                                "TITLE": OperatorConfig("redact", {})}
        )

        print(f"text: {anonymized_results.text}")
        print("detailed response:")
        pprint(anonymized_results)
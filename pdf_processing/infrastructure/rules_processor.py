import logging
import openai
import json
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class RulesProcessor:

	def __init__(self):
		self.openai_client = openai.AsyncOpenAI()
		self.model_name = "gpt-4o-mini"

	async def process_chapters(self,
	                           chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
		"""
				Process the chapters and extract rules.

				Args:
						chapters (List[Dict[str, Any]]): List of chapters extracted from the PDF.

				Returns:
						Dict[str, Any]: Structured output containing extracted rules and global rules.
				"""
		extracted_rules = []
		for chapter in chapters:
			try:
				rules = await self.extract_rules_from_text(chapter['content'])
				if rules:
					extracted_rules.extend(rules)
			except Exception as e:
				logger.error(f"Error processing chapter {chapter['number']}: {e}")

		return {
		    "rule_format_version": "1.0",  # Versioning of the rules format
		    "rules": extracted_rules,
		    "global_rules": {
		        "default_parameters": {},
		        "constraints": []
		    }
		}

	async def extract_rules_from_text(self, text: str) -> List[Dict[str, Any]]:
		"""
				Extract rules from a given text using OpenAI.

				Args:
						text (str): The text to analyze for rules.

				Returns:
						List[Dict[str, Any]]: A list of structured rules.
				"""
		messages = [{
		    "role":
		    "system",
		    "content":
		    ("You are an expert in extracting structured game rules from text. "
		     "Analyze the following content and identify all individual rules, then provide them "
		     "in the following JSON format without wrapping it in any code blocks (` ``` `):\n\n"
		     "{\n"
		     "  \"rules\": [\n"
		     "    {\n"
		     "      \"id\": A unique identifier for the rule,\n"
		     "      \"name\": A short descriptive title for the rule,\n"
		     "      \"description\": A detailed explanation of the rule,\n"
		     "      \"structure\": A list of entities involved in the rule (e.g., Player, Hit Points, Dice),\n"
		     "      \"behavior\": The logic or algorithm for the rule,\n"
		     "      \"logic\": A human-readable description of the rule's logic (can be translated to code),\n"
		     "      \"trigger\": When or how the rule activates (e.g., at the end of a turn),\n"
		     "      \"parameters\": Any modifiable values or thresholds associated with the rule,\n"
		     "      \"requirements\": Additional conditions or constraints for the rule to apply\n"
		     "    }\n"
		     "  ],\n"
		     "  \"global_rules\": {\n"
		     "    \"default_parameters\": Default parameters usable across multiple rules,\n"
		     "    \"constraints\": General constraints that apply to all rules\n"
		     "  }\n"
		     "}")
		}, {
		    "role":
		    "user",
		    "content":
		    f"Extract the rules from the following text:\n{text}"
		}]

		try:
			response = await self.openai_client.chat.completions.create(
			    model=self.model_name,
			    messages=messages,
			    temperature=0.0,
			    max_tokens=3000)
			raw_content = response.choices[0].message.content.strip()

			# Unwrap and validate JSON
			unwrapped_content = self._unwrap_json(raw_content)
			if self._is_valid_json(unwrapped_content):
				rules = json.loads(unwrapped_content).get("rules", [])
				logger.info(f"Extracted {len(rules)} rules from text.")
				return rules
			else:
				logger.warning(f"AI returned invalid JSON for rules: {raw_content}")
				return []

		except Exception as e:
			logger.error(f"Error extracting rules: {e}")
			return []

	@staticmethod
	def _unwrap_json(content: str) -> str:
		"""
				Remove wrapping delimiters such as ```markdown or ```json.

				Args:
						content (str): Content to clean.

				Returns:
						str: Cleaned JSON content.
				"""
		# Remove wrapping backticks and language indicators
		return re.sub(r'^```(?:json|markdown)?\n|```$',
		              '',
		              content,
		              flags=re.DOTALL).strip()

	@staticmethod
	def _is_valid_json(data: str) -> bool:
		"""
				Helper to check if a string is valid JSON.

				Args:
						data (str): Input string.

				Returns:
						bool: True if valid JSON, False otherwise.
				"""
		try:
			json.loads(data)
			return True
		except json.JSONDecodeError:
			return False

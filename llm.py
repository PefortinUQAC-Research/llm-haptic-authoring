from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage


class LLMClass:
    def __init__(self, settings):
        self.settings = settings

        self.temperature = self.settings.get("temperature", "")
        self.url = self.settings.get("api_url", "")
        self.api_key = self.settings.get("api_key", "")
        self.model_name = self.settings.get("model_name", "")

        self.llm = ChatOllama(
            temperature = self.temperature,
            base_url = self.url,
            client_kwargs={"headers": {"Authorization": f"Bearer {self.api_key}"}},
            model = self.model_name
        )
        pass

    def update_llm_settings(self, temperature, url, api_key, model_name):
        self.llm = self.llm = ChatOllama(
            temperature = temperature,
            base_url = url,
            client_kwargs={"headers": {"Authorization": f"Bearer {self.api_key}"}},
            model = model_name
        )

    def test_llm_connection(self):
        """Tests the connection to the specified LLM and updates the connection status."""
        try:
            messages = [HumanMessage(content="Test")]
            response = self.llm.invoke(messages)
            
            if response:
                return True
            else:
                return False
        except Exception:
            return False
        
    # Function to get description prompt from LLM via LM Studio
    def generate_description_prompt1(self, user_input):
        messages = [
            SystemMessage(content=(
                "You will be given a short description of a tactile sensation, which you will translate and describe as a vibrotactile "
                "haptic feedback using audio terminology."
            )),
            SystemMessage(content=(
                "You're an Audio Engineer with 20 years of experience. Your specialization is in creating audio files that will be used "
                "to create vibrotactile haptic feedbacks in video games and XR experiences."
            )),
            SystemMessage(content=(
                "Example:\n"
                "prompt given: Heartbeat\n"
                "Output: {\n"
                "  \"name\": \"heartbeat\",\n"
                "  \"description\": \"A rhythmic, low-frequency pulse. Use two short, sharp vibrations followed by a longer pause to mimic "
                "the 'lub-dub' rhythm of a heartbeat. The first pulse should be slightly stronger and quicker than the second, "
                "with a soft decay. The frequency should be around 60-80 BPM.\",\n"
                "  \"duration\": 1.5\n"
                "}"
            )),
            SystemMessage(content=(
                "Output Format:\n"
                "Output your answer in JSON format with exactly three keys:\n"
                "- \"name\": a short, descriptive identifier for the sensation, formatted in lowercase and suitable for use as a filename.\n"
                "- \"description\": a string containing the vibrotactile haptic feedback description.\n"
                "- \"duration\": a float representing the estimated duration in seconds."
            )),
            HumanMessage(content=f"prompt: {user_input}")
        ]
        
        response = self.llm.invoke(messages)
        return response.content  # Extract the description from the LLM response
    
    def generate_description_prompt2(self, description):
        messages = [
            SystemMessage(content=(
                "You will be given an elaborate description of a vibrotactile haptic feedback which uses audio terminology. "
                "Your role will then be to take this description and imagine an 'everyday' sound which audio-wise is similar."
            )),
            SystemMessage(content=(
                "You're an Audio Engineer with 20 years of experience. Your specialization is in creating audio files "
                "which in turn are going to be used to create vibrotactile haptic feedbacks in video games and XR experiences."
            )),
            # SystemMessage(content=(
            #     "Your descriptions of vibrotactile haptic feedback should focus on rhythm and tempo as much as timbre."
            # )),
            SystemMessage(content=(
                "Example:\n"
                "prompt given: A soft, dampened, mid-frequency vibration with a cushioned texture.\n"
                "Output: {\n"
                "  \"description\": \"A soft thump, like a plush toy being gently dropped onto a thick carpet.\"\n"
                "}"
            )),
            SystemMessage(content=(
                "Output your answer in JSON format. There should be 1 value: the outputted description of the vibrotactile haptic "
                "as a string."
            )),
            SystemMessage(content=(
                "Important: Avoid high-pitched sounds as these may not be felt clearly."
            )),
            HumanMessage(content=f"prompt: {description}")
        ]

        response = self.llm.invoke(messages)
        return response.content  # Extract the description from the LLM response
    
    def generate_edited_prompt(self, current_json, instructions):
        messages = [
            SystemMessage(content=(
                "You are given a JSON object describing vibrotactile haptic feedback. "
                "Your task is to modify this JSON strictly according to the user-provided instructions. "
                "Your response must be formatted as a JSON object only, with no additional text or explanations."
            )),
            SystemMessage(content=(
                "Important Instructions:\n"
                "1. Make changes only as described in the user's instructions.\n"
                "2. Retain the original JSON structure.\n"
                "3. Ensure the output is valid JSON, with all changes implemented exactly as requested.\n"
                "4. Do not add any descriptive text outside of the JSON."
            )),
            HumanMessage(content=(
                f"Original JSON:\n{current_json}\n\n"
                f"User Instructions:\n{instructions}"
            ))
        ]

        response = self.llm.invoke(messages)
        return response.content # Extract the description from the LLM response




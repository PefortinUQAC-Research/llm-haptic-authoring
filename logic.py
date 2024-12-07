from audiocraft.models import AudioGen


class VibrotactileGenerator:
    def __init__(self):
        self.model = AudioGen.get_pretrained('facebook/audiogen-medium')
        pass

    def update_model_settings(self, duration):
        self.model.set_generation_params(
                use_sampling=True,
                top_k=250,
                duration=duration
            )
        
    def generate_model(self, description):
        output = self.model.generate(
                descriptions=[description],
                progress=True
            )
        return output.cpu()

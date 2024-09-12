import os
import logging
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from modelscope import snapshot_download
from qwen_vl_utils import process_vision_info
import torch

class QwenVLModel:
    def __init__(self, model_dir="/path/to/your/qwen2-vl-model"):
        """Initializes the Qwen2-VL model and processor."""
        try:
            self.model_path = snapshot_download("qwen/Qwen2-VL-7B-Instruct", cache_dir=model_dir)
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                self.model_path, torch_dtype="auto", device_map="auto"
            )
            self.model.eval()  # Set the model to evaluation mode
            self.processor = AutoProcessor.from_pretrained(self.model_path)
            logging.info("Qwen2-VL model loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading Qwen2-VL model: {e}")
            raise  # Re-raise the exception to stop execution

    def process_video(self, video_frames, metadata, instruction="Describe this video."):
        """Processes a video using the Qwen2-VL model."""
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "video", "video": video_frames, "fps": metadata.get('fps', 1)},
                    {"type": "text", "text": instruction},
                ],
            }
        ]

        try:
            text = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            image_inputs, video_inputs = process_vision_info(messages)
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to("cuda" if torch.cuda.is_available() else "cpu")

            generated_ids = self.model.generate(**inputs, max_new_tokens=128)
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )
            return output_text[0]
        except Exception as e:
            logging.error(f"Error processing video with Qwen2-VL: {e}", exc_info=True)
            return None

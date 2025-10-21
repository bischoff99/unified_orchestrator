"""Test inference with trained LoRA model."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def test_inference(model_path="models/finetuned_gpt2", prompt="This movie was"):
    """Load LoRA model and generate text."""
    
    print("="*60)
    print("Testing LoRA Model Inference")
    print("="*60)
    print(f"Model: {model_path}")
    print(f"Prompt: {prompt}")
    print("="*60)
    
    try:
        # Load base model
        print("Loading base GPT-2 model...")
        base_model = AutoModelForCausalLM.from_pretrained("gpt2", device_map="mps", torch_dtype=torch.float16)
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        
        # Load LoRA adapter
        print(f"Loading LoRA adapter from {model_path}...")
        model = PeftModel.from_pretrained(base_model, model_path)
        model.eval()
        
        # Generate text
        print("\nGenerating text...")
        inputs = tokenizer(prompt, return_tensors="pt").to("mps")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=50,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )
        
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        print("\n" + "="*60)
        print("GENERATED TEXT:")
        print("="*60)
        print(generated_text)
        print("="*60)
        
        print("\n✅ Inference test passed!")
        print(f"   Generated {len(outputs[0]) - len(inputs['input_ids'][0])} new tokens")
        
        return {"status": "success", "text": generated_text}
        
    except Exception as e:
        print(f"\n❌ Inference failed: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    # Test with multiple prompts
    prompts = [
        "This movie was",
        "The acting in this film",
        "I really enjoyed",
    ]
    
    for prompt in prompts:
        print("\n")
        result = test_inference(prompt=prompt)
        if result["status"] != "success":
            exit(1)
        print("\n" + "-"*60)


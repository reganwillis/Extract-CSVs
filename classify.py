"""
Classify the documents as FDI or not using Qwen3 8B.
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


def load_classifier(quantize=True):
    model_name = "Qwen/Qwen3-8B"

    # load the tokenizer and the model
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    quantization_config = None
    if quantize:
        quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type='nf4',
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
        )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        #torch_dtype="auto",
        dtype=torch.float16,
        quantization_config=quantization_config,
        device_map="auto",
        low_cpu_mem_usage=True,
    )
    model.config.use_cache = False
    model.eval()

    return model, tokenizer


def classify(text, model, tokenizer, verbose=False):
    # prepare the model input
    prompt = "Classify if the following text is a foreign direct investment or not. Write \"True\" or \"False\" as the response: {" + text + "}"
    messages = [
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True
    )
    #model_inputs = tokenizer([text], truncation=True, max_length=120000, add_special_tokens=False, return_tensors="pt").to(model.device)
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    if model_inputs['input_ids'].shape[1] >= 16000:
        print('WARN: input too long, skipping..')
        return False
    #print('Classifying..')

    # conduct text completion
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=32768,
        do_sample=False
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

    # parsing thinking content
    try:
        # rindex finding 151668 (</think>)
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

    if verbose:
        print("thinking content:", thinking_content)
        print("content:", content)

    if content.strip().lower() == 'true':
        return True
    return False


if __name__ == "__main__":
    classifier, tokenizer = load_classifier()

    #text = "Australia builds manufacturing facility in Mexico City."
    with open('example.txt', 'r') as f:
        text = f.read()

    res = classify(text, classifier, tokenizer, verbose=True)
    print(res)

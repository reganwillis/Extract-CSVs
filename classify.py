"""
Classify the documents as FDI or not using Qwen3 8B.
"""
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_classifier():
    model_name = "Qwen/Qwen3-8B"

    # load the tokenizer and the model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )

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
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    # conduct text completion
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=32768
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

    if bool(content) == True:
        return True
    return False


if __name__ == "__main__":
    classifier, tokenizer = load_classifier()

    #text = "Australia builds manufacturing facility in Mexico City."
    with open('example.txt', 'r') as f:
        text = f.read()

    res = classify(text, classifier, tokenizer, verbose=True)
    print(res)

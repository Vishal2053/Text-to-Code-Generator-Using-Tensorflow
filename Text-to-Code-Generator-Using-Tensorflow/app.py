import streamlit as st
from transformers import TFT5ForConditionalGeneration, RobertaTokenizer
import random
from datasets import load_dataset
from pathlib import Path
class Args:
    # define training arguments

    # MODEL
    model_type = 't5'
    tokenizer_name = 'Salesforce/codet5-base'
    model_name_or_path = 'Salesforce/codet5-base'

    # DATA
    train_batch_size = 8
    validation_batch_size = 8
    max_input_length = 48
    max_target_length = 128
    prefix = "Generate Python: "

    # OPTIMIZER
    learning_rate = 3e-4
    weight_decay = 1e-4
    warmup_ratio = 0.2
    adam_epsilon = 1e-8

    # TRAINING
    seed = 2022
    epochs = 20

    # DIRECTORIES
    output_dir = "D:/texttocodeusingtensorflow/runs/"
    logging_dir = f"{output_dir}/logs/"
    checkpoint_dir = f"checkpoint"
    save_dir = f"{output_dir}/saved_model/"
    cache_dir = '../working/'
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(logging_dir).mkdir(parents=True, exist_ok=True)
    Path(save_dir).mkdir(parents=True, exist_ok=True)


# initialize training arguments
args = Args()
def run_predict(args, text):
    # load saved finetuned model
    model = TFT5ForConditionalGeneration.from_pretrained(args.save_dir)
    # load saved tokenizer
    tokenizer = RobertaTokenizer.from_pretrained(args.save_dir) 
    
    # encode texts by prepending the task for input sequence and appending the test sequence
    query = args.prefix + text 
    encoded_text = tokenizer(query, return_tensors='tf', padding='max_length', truncation=True, max_length=args.max_input_length)
    
    # inference
    generated_code = model.generate(
        encoded_text["input_ids"], attention_mask=encoded_text["attention_mask"], 
        max_length=args.max_target_length, top_p=0.95, top_k=50, repetition_penalty=1.5, num_return_sequences=1
    )
    
    # decode generated tokens
    decoded_code = tokenizer.decode(generated_code.numpy()[0], skip_special_tokens=True)
    return decoded_code

# Function to load the dataset
def predict_from_dataset(args):
    # load using hf datasets
    dataset = load_dataset('json', data_files=r"C:\Users\admin\Downloads\mbpp.jsonl") 
    # train test split
    dataset = dataset['train'].train_test_split(0.1, shuffle=False) 
    test_dataset = dataset['test']
    
    # randomly select an index from the validation dataset
    index = random.randint(0, len(test_dataset))
    text = test_dataset[index]['text']
    code = test_dataset[index]['code']
    
    # run-predict on text
    decoded_code = run_predict(args, text)
    
    return text, code, decoded_code

# Streamlit App
st.title("Text-to-Code Generator")

menu = ["Text Input", "Random Example from Dataset"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Text Input":
    st.subheader("Generate Code from Text")
    user_input = st.text_area("Enter text here:")
    if st.button("Generate Code"):
        args = st.text_input("Input model directory:")  # Assume the model directory is input by the user
        args = {
            "save_dir": args,
            "prefix": "translate English to code: ",
            "max_input_length": 256,
            "max_target_length": 256
        }
        generated_code = run_predict(args, user_input)
        st.code(generated_code, language="python")

elif choice == "Random Example from Dataset":
    st.subheader("Example from Dataset")
    if st.button("Generate Example"):
        args = st.text_input("Input model directory:")
        args = {
            "save_dir": args,
            "prefix": "translate English to code: ",
            "max_input_length": 256,
            "max_target_length": 256
        }
        text, code, generated_code = predict_from_dataset(args)
        st.write("### Query")
        st.write(text)
        st.write("### Original Code")
        st.code(code, language="python")
        st.write("### Generated Code")
        st.code(generated_code, language="python")

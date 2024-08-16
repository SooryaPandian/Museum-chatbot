import torch
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline

# Load pre-trained BERT model and tokenizer
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)

# Example sentences for sentiment analysis
sentences = [
    "I love this movie!",
    "This is the worst product I have ever bought."
]

# Tokenize sentences and convert to input IDs and attention masks
inputs = tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")

# Perform prediction
with torch.no_grad():
    outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=-1)

# Map prediction labels to sentiment
labels = ["Negative", "Positive"]
results = [labels[pred] for pred in predictions]

# Print results
for sentence, result in zip(sentences, results):
    print(f"Sentence: {sentence} \nSentiment: {result}\n")

# Alternatively, use the Hugging Face pipeline for sentiment analysis
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
results = classifier(sentences)

for result in results:
    print(f"Label: {result['label']}, Score: {result['score']:.4f}")
